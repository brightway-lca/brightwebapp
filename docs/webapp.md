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