# Docker and FastAPI

## Docker Setup

Build the Docker image:

!!! note
    Replace `<image_name>` with your desired image name.

```bash
docker build -t <image_name>:latest .
```

Spin up a docker container and bind the port 8000 to localhost:

```bash
docker run -d -p 8000:8000 <image_name>:latest
```

## Test USEEIO Database Operations

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

## Test Ecoinvent Database Operations

The Ecoinvent database can be tested with the FastAPI server. The following command sets up the database in the Docker instance:

```bash
curl -X POST http://localhost:8080/setup/ecoinvent-database \
-H "Content-Type: application/json" \
-d '{
        "username": "MichaelWeinold",
        "password": "jaqpaj-Mippuw-8hyjhe"
    }'
```

## Update Documentation

```bash
uvicorn api.main:app --reload
```

```
http://localhost:8000/openapi.json
```