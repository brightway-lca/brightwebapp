# ---- Stage 1: Build dependencies ----
# This stage installs dependencies into a specific directory.
# It's only re-run if pyproject.toml changes.
FROM python:3.9-slim as builder

WORKDIR /app

# Upgrade pip for better pyproject.toml support
RUN pip install --upgrade pip

# Copy only the project file to leverage Docker layer caching
COPY pyproject.toml .

# Install dependencies into a target directory. This does not install
# optional-dependencies (like 'testing') by default.
RUN pip install --no-cache-dir --prefix="/install" .

# ---- Stage 2: Create the final production image ----
# This stage copies the installed dependencies and your source code.
FROM python:3.9-slim

WORKDIR /app

# Copy the installed packages from the builder stage into the final image
COPY --from=builder /install /usr/local

# Copy your application source code
# Make sure your package name 'brightwebapp' is correct here.
COPY brightwebapp/ ./brightwebapp
COPY api/ ./api

# Expose the port the API will run on
EXPOSE 80

# The command to run your API using Uvicorn
# It looks for the 'app' object in the 'api.main' module.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]