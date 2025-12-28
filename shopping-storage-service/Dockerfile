# Build context should be the project root directory.
# Example: docker build -t shopping-storage-service -f shopping-storage-service/Dockerfile .

# Stage 1: Build stage - To build Python dependencies
FROM python:3.13-slim as builder

WORKDIR /api

# Install build-time dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc

# Copy requirements file for shopping-storage-service
COPY shopping-storage-service/requirements.txt .

# Copy shared/ as a real top-level package (code imports `shared.shopping_shared...`)
COPY shared/ /api/shared

# Build wheel for shared package first (with fastapi extra)
RUN pip wheel --no-cache-dir --wheel-dir /api/wheels ./shared[fastapi]

# Build wheels for all other requirements
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

# Copy shared package from builder stage (needed at runtime for imports)
COPY --from=builder --chown=appuser:appuser /api/shared ./shared

# Install all dependencies from local wheels (including shopping-shared)
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*

# Copy the application code for the shopping-storage-service
# Copy main.py and alembic files
COPY --chown=appuser:appuser shopping-storage-service/main.py .
COPY --chown=appuser:appuser shopping-storage-service/alembic.ini .
COPY --chown=appuser:appuser shopping-storage-service/alembic/ ./alembic/

# Copy src directory (contains core, apis, messaging, etc.)
COPY --chown=appuser:appuser shopping-storage-service/src/ ./src/

# Set PYTHONPATH so both `core/...` and `shared.shopping_shared/...` imports work
ENV PYTHONPATH=/api:/api/src:${PYTHONPATH}

# Expose the application port (matching main.py)
EXPOSE 8002

# Use dumb-init as the entrypoint to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Command to run the application
CMD ["python3", "main.py"]


