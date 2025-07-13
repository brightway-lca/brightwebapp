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

### Converting to Pyodide Web Application

Panel applications can be converted to a web application that runs in the browser using [Pyodide](https://pyodide.org/en/stable/index.html) (Python in the browser) with [the `panel convert` command](https://panel.holoviz.org/how_to/wasm/convert.html):

```bash
panel convert app/index.py --to pyodide-worker --out pyodide
```

This will create a directory `pyodide` containing an `index.html` file and a `worker.js` file, which can be served by any web server:

```bash
python -m http.server
```

### Dependency Management

!!! note
    
    All dependencies of the web application must be installed in the virtual environment from which the `panel convert` command is called.

[Pyodide](https://pyodide.org/en/stable/index.html) is a monolithic distribution of Python, which means that it ships with a specific set of Python packages and versions. The versions of the packages are fixed and cannot be changed. The list of packages and their versions are listed under ["Packages in Pyodide"](https://pyodide.org/en/stable/usage/packages-in-pyodide.html).

#### Specifying the Pyodide Version

Panel does not currently support specifying the Pyodide version to use for the conversion. The version of Pyodide used [is hardcoded in `panel.io.convert`](https://github.com/holoviz/panel/blob/0eb8909c3ed3d8c964da6eed7cd4c2167488d058/panel/io/convert.py#L44). However, the Pyodide version can be manually changed by modifying first line of the `index.js` file in the `pyodide` directory after the conversion:

```javascript
importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.5/full/pyodide.js");
```

#### Specifying Dependencies

After converting the web application using `panel convert`, the dependencies (=Python packages) which Pyodide must load from PyPi are listed in the file `index.js` in the function `startApplication()` under:

```javascript hl_lines="8"
async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.7.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.7.1/dist/wheels/panel-1.7.1-py3-none-any.whl', 'pyodide-http==0.2.1', 'lzma', 'typing-extensions', 'brightwebapp==0.0.6']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
(...)
```

By default, Panel _infers_ the dependencies from the Python code of the web application, but this can be overridden by specifying the `--requirements` option.

!!! warning

    The Pyodide distribution [has removed some large-size modules of the Python standard library](https://pyodide.org/en/stable/usage/wasm-constraints.html#optional-modules) to reduce the initial download size, including `ssl`, `lzma`, `sqlite3`, and `test`.
    
    If your application uses any of these modules, you **must** make sure they are listed in the `index.js`. For this, you must use a requirements file to specify the packages explicitly and pass the file to the `--requirements` option of the `panel convert` command:

    ```bash
    panel convert app/index.py --to pyodide-worker --out pyodide --requirements app/requirements_pyodide_conversion.txt
    ```

#### Pinning ALL Dependencies for Maximum Reproducibility

Why would I need this?
How can I best do this?

### Running Python Code before the Application Loads

Arbitrary Python code can be run before the web application loads by modifying the `index.js` file in the `pyodide` directory after the conversion. Python code can be wrapped in a `await self.pyodide.runPythonAsync` block and moved to arbitrary places in the `startApplication()` function:

```javascript hl_lines="18-22"
async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.7.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.7.1/dist/wheels/panel-1.7.1-py3-none-any.whl', 'pyodide-http==0.2.1', 'lzma', 'typing-extensions', 'brightwebapp==0.0.6']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }
(...)
```