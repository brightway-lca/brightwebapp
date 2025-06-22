# Web Application

## Pyodide (Python in the Browser)

### Converting

Which packages must be installed in the venv from which the conversion is made?

```bash
panel convert app/index.py --to pyodide-worker --out pyodide --requirements app/requirements_pyodide_conversion.txt
```

### Testing

```bash
python -m http.server
```

###

Since [Pyodide ships with `numpy>2.0.0`](https://pyodide.org/en/stable/usage/packages-in-pyodide.html),
the files must be manually edited:

The latest version still using <2.0.0 was https://pyodide.org/en/0.26.4/usage/packages-in-pyodide.html