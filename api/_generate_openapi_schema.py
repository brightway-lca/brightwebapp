# run this script to generate the OpenAPI schema for the FastAPI application
# it will create a file named openapi.json in the current directory
# python -m api._generate_openapi_schema

import json
from .main import app

openapi_schema = app.openapi()

with open("openapi.json", "w") as f:
    json.dump(openapi_schema, f, indent=2)

print("✅ OpenAPI schema saved to openapi.json")