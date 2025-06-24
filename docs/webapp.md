# Web Application Development

## Pyodide (Python in the Browser)

### Converting to Pyodide Web Application

!!! info

    Panel Documentation: ["Converting Panel Applications"](https://panel.holoviz.org/how_to/wasm/convert.html)

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

#### Pyodide Python Package Versions

Pyodide is a monolithic distribution of Python, which means that it ships with a specific set of Python packages and versions. The versions of the packages are fixed and cannot be changed. The list of packages and their versions are listed under ["Packages in Pyodide"](https://pyodide.org/en/stable/usage/packages-in-pyodide.html).

#### Specifying the Pyodide Version

Panel does not currently support specifying the Pyodide version to use for the conversion. The version of Pyodide used [is hardcoded in `panel.io.convert`](https://github.com/holoviz/panel/blob/0eb8909c3ed3d8c964da6eed7cd4c2167488d058/panel/io/convert.py#L44). However, the Pyodide version can be manually changed by modifying first line of the `index.js` file in the `pyodide` directory after the conversion:

```javascript
importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.5/full/pyodide.js");
```

#### Specifying Dependencies

After converting the web application using `panel convert`, the dependencies (=Python packages) which Pyodide must load from PyPi are listed in the file `index.js` in the function `startApplication()` under:

```javascript
const env_spec = [
    'https://cdn.holoviz.org/panel/wheels/bokeh-3.7.3-py3-none-any.whl',
    'https://cdn.holoviz.org/panel/1.7.1/dist/wheels/panel-1.7.1-py3-none-any.whl',
    'pyodide-http==0.2.1',
    'brightwebapp',
    'bw2data',
    'pandas',
    'plotly'
]
```

By default, Panel _infers_ the dependencies from the Python code of the web application, but this can be overridden by specifying the `--requirements` option.

!!! warning

    The Pyodide distribution [has removed some large-size modules of the Python standard library](https://pyodide.org/en/stable/usage/wasm-constraints.html#optional-modules) to reduce the initial download size:

    - ssl
    - lzma
    - sqlite3
    - test

    If your application uses any of these modules, you **must** make sure they are listed in the `index.js`. For this, you must use a requirements file to specify the packages explicitly and pass the file to the `--requirements` option of the `panel convert` command:

    ```bash
    panel convert app/index.py --to pyodide-worker --out pyodide --requirements app/requirements_pyodide_conversion.txt
    ```