"""
Builds the Pyodide web application in `pyodide/` from `app/index.py`.

`panel convert` generates a web worker (`index.js`) which resolves all requirements
from PyPI with `micropip` on every page load. Any new release of any (transitive) dependency
can therefore break the deployed web application. This script instead:

1. converts `app/index.py` with `panel convert` and the requirements in `app/requirements.txt`,
2. resolves these requirements once in Pyodide (in a headless browser)
   and freezes the result to `pyodide/pyodide-lock.json` (only with `--lock`),
3. rewrites `index.js` to load exactly the locked package versions from this lock file.

Usage (from the repository root):

```bash
pip install -e ".[webapp]"
playwright install chromium
python app/build.py --lock # after changing app/requirements.txt: re-resolve all package versions
python app/build.py # after changing app/index.py: re-use the existing lock file
```

See Also
--------
- [Pyodide Documentation: `micropip.freeze`](https://micropip.pyodide.org/en/stable/project/api.html#micropip.freeze)
- [Pyodide Documentation: `loadPyodide(lockFileURL)`](https://pyodide.org/en/stable/usage/api/js-api.html#globalThis.loadPyodide)
"""
import argparse
import ast
import asyncio
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / 'app' / 'index.py'
REQUIREMENTS = ROOT / 'app' / 'requirements.txt'
OUT = ROOT / 'pyodide'
LOCK = OUT / 'pyodide-lock.json'
# Panel 1.7.1 defaults to Pyodide 0.27.5
PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.js'
# every Panel release overwrites the wheels in this unversioned directory
HOLOVIZ_SHARED_WHEELS = 'https://cdn.holoviz.org/panel/wheels/'

LOADER_PANEL = '''  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
'''
LOADER_LOCK = '''  try {{
    self.pyodide = await loadPyodide({{
      lockFileURL: new URL('{lock}', self.location.href).href
    }});
    self.pyodide.globals.set("sendPatch", sendPatch);
    console.log("Loaded!");
    self.postMessage({{type: 'status', msg: 'Loading packages'}})
    // nota bene: loadPackage does not throw if a package fails to load
    const errors = [];
    await self.pyodide.loadPackage({packages}, {{errorCallback: (msg) => errors.push(msg)}});
    if (errors.length) {{
      throw new Error(errors.join('\\n'));
    }}
  }} catch(e) {{
    self.postMessage({{type: 'status', msg: `Error while loading packages: ${{e.message}}`}});
    throw e;
  }}
'''


def convert(out: Path) -> tuple[str, str]:
    """
    Converts `app/index.py` with `panel convert` to the directory `out`
    and returns the content of the generated `index.html` and `index.js`.
    """
    subprocess.run(
        [
            sys.executable, '-m', 'panel', 'convert', str(APP),
            '--to', 'pyodide-worker',
            '--out', str(out),
            '--requirements', str(REQUIREMENTS),
        ],
        check=True,
    )
    # nota bene: `panel convert` exits with code 0 even if the conversion fails
    if not (out / 'index.html').exists() or not (out / 'index.js').exists():
        sys.exit('panel convert failed, see the output above.')
    return (out / 'index.html').read_text(), (out / 'index.js').read_text()


def read_env_spec(js: str) -> list[str]:
    """
    Returns the requirements (`env_spec`) which `panel convert` wrote to `index.js`,
    with the wheels from the unversioned HoloViz CDN directory replaced by the copies in the versioned Panel release directory, e.g.:

    ```python
    ['https://cdn.holoviz.org/panel/1.7.1/dist/wheels/bokeh-3.7.3-py3-none-any.whl', ..., 'pyodide-http==0.2.1', 'lzma', 'brightwebapp==1.0.1']
    ```
    """
    match = re.search(r"^  const env_spec = (\[.*\])$", js, re.MULTILINE)
    if match is None:
        sys.exit('Could not find `env_spec` in index.js. Has the Panel template changed?')
    env_spec = ast.literal_eval(match.group(1))
    panel_wheel = next(requirement for requirement in env_spec if parse(requirement)[0] == 'panel')
    return [requirement.replace(HOLOVIZ_SHARED_WHEELS, panel_wheel.rsplit('/', 1)[0] + '/') for requirement in env_spec]


def parse(requirement: str) -> tuple[str, str | None, SpecifierSet]:
    """
    Returns the canonical package name, URL and version specifier of a requirement,
    which is either a requirement string (e.g. `brightwebapp==1.0.1` or `brightwebapp @ https://.../brightwebapp-1.0.1-py3-none-any.whl`)
    or a wheel URL (e.g. `https://.../bokeh-3.7.3-py3-none-any.whl`).
    """
    try:
        parsed = Requirement(requirement)
    except InvalidRequirement:
        return canonicalize_name(requirement.rsplit('/', 1)[-1].split('-')[0]), requirement, SpecifierSet()
    return canonicalize_name(parsed.name), parsed.url, parsed.specifier


async def resolve(env_spec: list[str]) -> dict:
    """
    Installs the requirements with `micropip` in Pyodide in a headless browser
    and returns the resulting Pyodide lock file (from `micropip.freeze()`).
    """
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.add_script_tag(url=PYODIDE_URL)
        lock = await page.evaluate(
            '''async (env_spec) => {
                const pyodide = await loadPyodide();
                await pyodide.loadPackage('micropip');
                const micropip = pyodide.pyimport('micropip');
                await micropip.install(pyodide.toPy(env_spec));
                return micropip.freeze();
            }''',
            env_spec,
        )
        await browser.close()
    return json.loads(lock)


def check_lock(lock: dict, env_spec: list[str]) -> None:
    """
    Checks that the lock file was resolved with the Pyodide version in `PYODIDE_URL` and satisfies every requirement,
    so that a changed `app/requirements.txt` is never silently deployed with an outdated lock file.
    """
    pyodide_packages = PYODIDE_URL.rsplit('/', 1)[0] + '/'
    for package in lock['packages'].values():
        if package['file_name'].startswith('https://cdn.jsdelivr.net/pyodide/') and not package['file_name'].startswith(pyodide_packages):
            sys.exit(f'{LOCK.name} was resolved with another Pyodide version than {PYODIDE_URL}. Run `python app/build.py --lock`.')
    for requirement in env_spec:
        name, url, specifier = parse(requirement)
        package = lock['packages'].get(name)
        if package is None:
            sys.exit(f'{name} is missing from {LOCK.name}. Run `python app/build.py --lock`.')
        if url is None:
            # a requirement without URL must have been resolved from PyPI or the Pyodide distribution
            url_matches = package['file_name'].startswith(('https://files.pythonhosted.org/', pyodide_packages))
        else:
            url_matches = package['file_name'] == url
        if not url_matches or not specifier.contains(package['version'], prereleases=True):
            sys.exit(f'{requirement} does not match {name}=={package["version"]} from {package["file_name"]} in {LOCK.name}. Run `python app/build.py --lock`.')


def patch(js: str, env_spec: list[str], lock: str) -> str:
    """
    Rewrites `index.js` to load Pyodide from `PYODIDE_URL`
    and all packages from the lock file, instead of installing them with `micropip`.

    The lock file URL contains a hash of the lock file,
    so that browsers and CDNs never combine a new `index.js` with a cached, outdated lock file.
    """
    js, count = re.subn(r'^importScripts\("[^"]+"\);$', f'importScripts("{PYODIDE_URL}");', js, count=1, flags=re.MULTILINE)
    start = js.find(LOADER_PANEL)
    end = js.find('  console.log("Packages loaded!");')
    if count != 1 or start == -1 or end == -1:
        sys.exit('Could not patch index.js. Has the Panel template changed?')
    loader = LOADER_LOCK.format(
        lock=f'{LOCK.name}?v={hashlib.sha256(lock.encode()).hexdigest()[:12]}',
        packages=json.dumps([parse(requirement)[0] for requirement in env_spec]),
    )
    return js[:start] + loader + js[end:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--lock', action='store_true', help=f're-resolve all package versions and rewrite {LOCK.name}')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        html, js = convert(Path(tmp))
    env_spec = read_env_spec(js)
    if args.lock:
        lock = json.dumps(asyncio.run(resolve(env_spec)), indent=2, sort_keys=True) + '\n'
    elif LOCK.exists():
        lock = LOCK.read_text()
    else:
        sys.exit(f'{LOCK.name} does not exist. Run `python app/build.py --lock`.')
    check_lock(json.loads(lock), env_spec)
    js = patch(js, env_spec, lock)
    # write the output only after all checks have passed, so that a failed build never leaves an unpatched `index.js`
    OUT.mkdir(exist_ok=True)
    (OUT / 'index.html').write_text(html, newline='\n')
    (OUT / 'index.js').write_text(js, newline='\n')
    LOCK.write_text(lock, newline='\n')
    print(f'Built the web application in {OUT.relative_to(ROOT)}/ from {len(env_spec)} requirements.')


if __name__ == '__main__':
    main()
