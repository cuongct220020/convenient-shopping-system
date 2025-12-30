# Stage 1: Builder
FROM python:3.13-slim as builder

WORKDIR /app/user-service

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared module and requirements
COPY shared /app/shared
COPY user-service/requirements.txt .

# Remove editable local requirement to build it as a standard wheel
# This prevents pip from trying to locate ../shared in the editable way during wheel build
RUN sed -i '/-e ..\/shared/d' requirements.txt

# Build wheels for dependencies and the shared library
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt \
    && pip wheel --no-cache-dir --wheel-dir /app/wheels /app/shared

# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app/user-service

# Install runtime utilities (dumb-init for signal handling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels

# Install dependencies from wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*

# Copy application code
COPY --chown=appuser:appuser user-service .

USER appuser

# Expose port (Internal Sanic port)
EXPOSE 9000

# Use dumb-init for proper signal handling (PID 1)
ENTRYPOINT ["dumb-init", "--"]

# Command to run the application
CMD ["python3", "run.py"]