# Build context should be the project root directory.
# Example: docker build -t user-service -f microservices/user-service/Dockerfile .

# Stage 1: Build stage - To build Python dependencies
FROM python:3.13-slim as builder

WORKDIR /api

# Install build-time dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc

# Copy requirements file for user-service
COPY microservices/user-service/requirements.txt .

# Copy the entire shared package so we can install it
COPY shared/ /api/shopping_shared

# Install the shared package first as a wheel, then the rest of the requirements.
# This makes the 'shopping-shared' package available for the next step.
RUN pip wheel --no-cache-dir --wheel-dir /api/wheels -e ./shopping_shared
RUN pip wheel --no-cache-dir --wheel-dir /api/wheels -r requirements.txt


# Stage 2: Final stage - The actual runtime image
FROM python:3.13-slim

WORKDIR /api

# Install dumb-init to handle signals properly
RUN apt-get update && apt-get install -y --no-install-recommends dumb-init && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Copy pre-built wheels from the builder stage
COPY --from=builder /api/wheels /wheels

# Install all dependencies from local wheels
# This will install 'shopping-shared' and all other packages.
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*

# Copy the application code for the user-service
COPY --chown=appuser:appuser microservices/user-service/ .

# Copy shared package
COPY --chown=appuser:appuser shared/ ./shopping_shared

# Expose the application port (matching docker-compose.yml)
EXPOSE 8000

# Use dumb-init as the entrypoint to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Command to run the application
CMD ["python3", "main.py"]
