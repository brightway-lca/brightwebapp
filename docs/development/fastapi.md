# Docker and FastAPI

This page provides information on how to set up a Docker container with FastAPI for developing and testing Brightway-enabled web applications.

## Docker Setup (static)

Build the Docker image based on the provided `Dockerfile`:

!!! note
    Replace `brightapp` with your desired image name.

```bash
docker build -t brightapp:latest .
```

Spin up a docker container and bind the port 8000 to localhost:

```bash
docker run -d -p 8000:8000 brightapp:latest
```

## Docker Setup (dynamic)

For a more dynamic setup, you can use the `docker-compose.yml` file. This allows you to easily manage the container and its dependencies.
It also mounts the current directory to the `/app` directory in the container, allowing you to develop and test your application without rebuilding the image every time you make a change.

```bash
docker-compose up --build
```

## Test USEEIO Database Operations

The USEEIO database can be tested with the FastAPI server. The following command sets up the database in the Docker instance:

```bash
curl -X POST http://localhost:8000/setup/useeio-database
```

A simple path traversal calculation can be performed with the following command:

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
curl -X POST http://localhost:8000/setup/ecoinvent-database \
-H "Content-Type: application/json" \
-d '{
        "username": "MichaelWeinold",
        "password": "PASSWORD"
    }'
```

An arbitrary Ecoinvent node can be retrieved by its [`code` field](https://github.com/brightway-lca/brightway2-data/blob/2b71aec652d29d367ea2c166c78dafd4c90e1397/bw2data/utils.py#L355) with the following command:

```bash
curl -X GET "http://localhost:8000/database/getnode?code=43ec7ae3d4442a295564dd4a24906725"
```

A simple path traversal calculation can be performed with the following command:

```bash
curl -X POST http://localhost:8000/traversal/perform \
-H "Content-Type: application/json" \
-d '{
        "demand": [
            {
                "code": "43ec7ae3d4442a295564dd4a24906725",
                "amount": 1
            }
        ],
        "method": [
            "ecoinvent-3.10",
            "CML v4.8 2016",
            "climate change",
            "global warming potential (GWP100)"
        ],
        "cutoff": 0.001,
        "biosphere_cutoff": 0.001,
        "max_calc": 15
    }' \
--output traversal_result.csv
```

## Update API ([Swagger UI](https://swagger.io)) Documentation

The FastAPI server provides an OpenAPI documentation endpoint that can be accessed at:

```
http://localhost:8000/docs
```

with the underlying OpenAPI schema available at:

```
http://localhost:8000/openapi.json
```

A simple helper script `api/_generate_openapi_schema.py` is provided to generate the OpenAPI schema from the FastAPI server:

```bash
python -m api._generate_openapi_schema
```

The generated OpenAPI schema will be saved in a file named `openapi.json` in the current directory and should be moved to the `docs/api` directory to be included in the documentation.