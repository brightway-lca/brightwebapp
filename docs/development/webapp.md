# Web Application Development

This page provides information on how to develop, debug and deploy Brightway-enabled web applications using the [Holoviz Panel library](https://panel.holoviz.org).

## Pyodide (Python in the Browser)

### Testing Pyodide Compatiblitiy

The compatibility of a Python package with Pyodide can be easily tested using [the Pyodide REPL in the browser](https://pyodide.org/en/stable/console.html), using [the usual installation process](https://pyodide.org/en/stable/usage/loading-packages.html):

```py
import micropip
await micropip.install('<PACKAGENAME==PACKAGEVERSION>')
```

!!! tip

    [Different versions of Pyodide](https://github.com/pyodide/pyodide/releases) can be specified by changing the URL in the browser address bar, e.g:
    
    ```
    https://pyodide.org/en/0.27.7/console.html
    https://pyodide.org/en/stable/console.html
    https://pyodide.org/en/latest/console.html
    ```

### Building the Pyodide Web Application

Panel applications can be converted to a web application that runs in the browser using [Pyodide](https://pyodide.org/en/stable/index.html) (Python in the browser) with [the `panel convert` command](https://panel.holoviz.org/how_to/wasm/convert.html). The script `app/build.py` wraps this command and builds the web application in the `pyodide` directory:

```bash
pip install -e ".[webapp]"
playwright install chromium
python app/build.py --lock # after changing app/requirements.txt: re-resolve all package versions
python app/build.py # after changing app/index.py: re-use the existing lock file
```

This creates the files `index.html`, `index.js` (the web worker running Pyodide) and `pyodide-lock.json` in the `pyodide` directory, which can be served by any web server:

```bash
python -m http.server --directory pyodide
```

Before deploying, test the web application end-to-end in a headless browser:

```bash
python app/smoke_test.py pyodide # tests the local build
python app/smoke_test.py https://webapp.brightway.dev # tests the deployed web application
```

!!! note

    Pushing changes to the `pyodide` directory to the `main` branch deploys the web application to [webapp.brightway.dev](https://webapp.brightway.dev) through GitHub Pages, but only if the smoke test passes. Pull requests which change the `app` or `pyodide` directories are also checked for an outdated build (`app/build.py` must reproduce the committed `pyodide/index.js` and `pyodide/pyodide-lock.json`).

    The smoke test also runs against the deployed web application once a week. Note that GitHub disables scheduled workflows after 60 days without activity in the repository; re-enable the "Test Web Application" workflow in the "Actions" tab if necessary.

### Dependency Management

!!! note
    
    All dependencies of the web application must be installed in the virtual environment from which `app/build.py` is called, since `panel convert` executes `app/index.py`.

[Pyodide](https://pyodide.org/en/stable/index.html) is a monolithic distribution of Python, which means that it ships with a specific set of Python packages and versions. The versions of the packages are fixed and cannot be changed. The list of packages and their versions are listed under ["Packages in Pyodide"](https://pyodide.org/en/stable/usage/packages-in-pyodide.html). All other (pure Python) packages are loaded from PyPI.

#### Specifying the Pyodide Version

Panel does not currently support specifying the Pyodide version to use for the conversion. The version of Pyodide used [is hardcoded in `panel.io.convert`](https://github.com/holoviz/panel/blob/0eb8909c3ed3d8c964da6eed7cd4c2167488d058/panel/io/convert.py#L44). `app/build.py` therefore replaces it with the version set in `PYODIDE_URL`:

```python
PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.js'
```

After changing the Pyodide version, the lock file must be re-resolved with `python app/build.py --lock`.

#### Specifying Dependencies

The Python packages required by the web application are listed in `app/requirements.txt`. Panel adds its own requirements (`bokeh`, `panel` and `pyodide-http`).

!!! warning

    The Pyodide distribution [has removed some large-size modules of the Python standard library](https://pyodide.org/en/stable/usage/wasm-constraints.html#optional-modules) to reduce the initial download size, including `ssl`, `lzma`, `sqlite3`, and `test`.
    
    If your application uses any of these modules, you **must** list them in `app/requirements.txt`.

#### Pinning ALL Dependencies for Maximum Reproducibility

By default, `panel convert` generates a web worker which installs all requirements with [`micropip`](https://micropip.pyodide.org/) on every page load. Only the top-level requirements are pinned (e.g. `brightwebapp==1.0.1`), while all transitive dependencies are resolved from PyPI _at the time the page is loaded_. Any new release of any transitive dependency can therefore break the deployed web application, without any change to the web application itself. For example, the release of `typing-inspection==0.4.4` (which requires `typing-extensions>=4.15.0`, while Pyodide 0.28.2 ships with `typing-extensions==4.14.1`) broke the web application on load.

`app/build.py --lock` therefore resolves all requirements once in Pyodide (in a headless browser) and freezes the result with [`micropip.freeze()`](https://micropip.pyodide.org/en/stable/project/api.html#micropip.freeze) to the lock file `pyodide/pyodide-lock.json`. The lock file lists the exact version, URL and SHA-256 hash of every package. `app/build.py` then rewrites the web worker to load all packages from this lock file:

```javascript
self.pyodide = await loadPyodide({
  lockFileURL: new URL('pyodide-lock.json?v=6f9a95507a8f', self.location.href).href
});
(...)
await self.pyodide.loadPackage(["bokeh", "panel", "pyodide-http", "lzma", "brightwebapp"], {errorCallback: (msg) => errors.push(msg)});
```

The web application then loads exactly the same packages on every page load, until the lock file is re-resolved. Pyodide verifies the SHA-256 hash of every package, and the web application shows an error message if any package fails to load. The query string `?v=...` is a hash of the lock file, so that browsers and CDNs never combine a new `index.js` with a cached, outdated lock file.

`app/build.py` exits with an error (without changing the `pyodide` directory) if `app/requirements.txt` is not satisfied by the lock file, or if the lock file was resolved with another Pyodide version.

!!! note

    Panel requires the `bokeh` wheel from the HoloViz CDN directory `https://cdn.holoviz.org/panel/wheels/`, which is overwritten by every Panel release. `app/build.py` therefore uses the identical copy in the versioned directory of the Panel release (e.g. `https://cdn.holoviz.org/panel/1.7.1/dist/wheels/`).

### Running Python Code before the Application Loads

Arbitrary Python code can be run before the web application loads by wrapping it in a `await self.pyodide.runPythonAsync` block in the `startApplication()` function of the `index.js` file, e.g. after all packages have been loaded:

```javascript hl_lines="4-7"
async function startApplication() {
  (...)
  await self.pyodide.loadPackage(["bokeh", "panel", "pyodide-http", "lzma", "brightwebapp"]);
  await self.pyodide.runPythonAsync(`
    import brightwebapp
    print(brightwebapp.__version__)
  `);
  console.log("Packages loaded!");
(...)
```

!!! warning

    `app/build.py` regenerates `index.js` on every build. Such modifications must therefore be added to the `LOADER_LOCK` template in `app/build.py`.
