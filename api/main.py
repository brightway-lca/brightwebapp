from fastapi import FastAPI
from . import endpoints

app = FastAPI(
    title="BrightWebApp API",
    description="A web API for the BrightWebApp package.",
    version="1.0.0",
)

app.include_router(endpoints.router)