# Stage 1: Build stage - To build Python dependencies
FROM python:3.11-slim as builder

WORKDIR /api

# Install build-time dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Copy and install Python dependencies as wheels
COPY requirements.txt .
# The -e ../../shopping_shared in requirements.txt requires the shared folder to be present
# We will copy the whole project context for the build stage
COPY .. /
RUN pip wheel --no-cache-dir --wheel-dir /api/wheels -r requirements.txt


# Stage 2: Final stage - The actual runtime image
FROM python:3.11-slim

WORKDIR /api

# Create a non-root user and switch to it
RUN useradd --create-home appuser
USER appuser

# Copy pre-built wheels from the builder stage
COPY --from=builder /api/wheels /wheels

# Install the dependencies from local wheels
RUN pip install --no-cache-dir /wheels/*

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 1338

# Command to run the application
CMD ["python3", "main.py"]
