# FastAPI

## Test

The USEEIO database can be tested with the FastAPI server. The following command sets up the database in the Docker instance:

```bash
curl -X POST http://localhost:8000/setup/useeio-database
```

and:

```bash
curl -X POST 'http://localhost:8000/traversal/perform' \
-H 'Content-Type: application/json' \
-d '{
    "demand": [
        {
            "code": "5877b502-e197-33c2-815a-eac0934be16e",
            "amount": 1.0
        }
    ],
    "method": [
        "Impact Potential",
        "HC"
    ]
}' \
--output traversal_result.csv
```

## Update Documentation

```bash
uvicorn api.main:app --reload
```

```
http://localhost:8000/openapi.json
```