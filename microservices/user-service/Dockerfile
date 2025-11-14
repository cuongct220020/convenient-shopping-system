# Build context should be the project root directory.
# Example: docker build -t user-service -f microservices/user-service/Dockerfile .

# Stage 1: Build stage - To build Python dependencies
FROM python:3.13-slim as builder

WORKDIR /api

# Install build-time dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Copy requirements file for user-service
COPY microservices/user-service/requirements.txt .

# Copy the entire common package so we can install it
COPY shopping_shared /api/shopping_shared

# Install the common package first as a wheel, then the rest of the requirements.
# This makes the 'shopping-shared' package available for the next step.
RUN pip wheel --no-cache-dir --wheel-dir /api/wheels -e ./shopping_shared
RUN pip wheel --no-cache-dir --wheel-dir /api/wheels -r requirements.txt


# Stage 2: Final stage - The actual runtime image
FROM python:3.13-slim

WORKDIR /api

# Create a non-root user and switch to it
RUN useradd --create-home appuser
USER appuser

# Copy pre-built wheels from the builder stage
COPY --from=builder /api/wheels /wheels

# Install all dependencies from local wheels
# This will install 'shopping-common' and all other packages.
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*

# Copy the application code for the user-service
# The WORKDIR is /api, so this copies the service code into /api/app, /api/main.py etc.
COPY microservices/user-service/ .

# Expose the application port
EXPOSE 1337

# Command to run the application
CMD ["python3", "main.py"]
