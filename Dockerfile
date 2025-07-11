# ---- Stage 1: Build dependencies ----
# This stage installs dependencies into a specific directory.
# It's only re-run if pyproject.toml changes.
# https://docs.docker.com/reference/dockerfile/#from
FROM python:3.11-slim AS builder

# https://docs.docker.com/reference/dockerfile/#workdir
WORKDIR /app

# Upgrade pip for better pyproject.toml support
# https://docs.docker.com/reference/dockerfile/#run
RUN pip install --upgrade pip

# Copy only the project file to leverage Docker layer caching
COPY pyproject.toml .

# Copy the package source (now in src/brightwebapp; copied to /app/brightwebapp for consistency)
COPY src/brightwebapp/ ./brightwebapp

# Install the project with API extras (includes fastapi and uvicorn)
RUN pip install --no-cache-dir --prefix="/install" .[api]

# ---- Stage 2: Create the final production image ----
# This stage copies the installed dependencies and your source code.
FROM python:3.11-slim

WORKDIR /app

# Copy the installed packages from the builder stage into the final image
COPY --from=builder /install /usr/local

# Copy your application source code
# Make sure your package name 'brightwebapp' is correct here.
# https://docs.docker.com/reference/dockerfile/#copy
COPY src/brightwebapp/ ./brightwebapp
COPY api/ ./api

# Expose the port the API will run on
EXPOSE 8000

# The command to run your API using Uvicorn
# It looks for the 'app' object in the 'api.main' module.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]