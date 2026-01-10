# Stage 1: Dependencies Builder
FROM python:3.13-slim AS dependencies-builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and shared module
COPY shopping-storage-service/requirements.txt /app/requirements.txt
COPY shared /app/shared

# Filter requirements to remove editable shared package reference and install
RUN head -n -1 requirements.txt > requirements-docker.txt

RUN pip install --no-cache-dir /app/shared[fastapi] && \
    pip install --no-cache-dir -r requirements-docker.txt

# Stage 2: Runtime
FROM python:3.13-slim AS runtime

WORKDIR /app/shopping-storage-service

# Set timezone to Vietnam
RUN apt-get update && apt-get install -y --no-install-recommends \
    dumb-init \
    curl \
    ca-certificates \
    tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --system --gid 1001 appuser && \
    useradd --system --uid 1001 --gid 1001 --shell /bin/bash --create-home appuser

# Copy site-packages and binaries
COPY --from=dependencies-builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=dependencies-builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser shopping-storage-service/ /app/shopping-storage-service/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/shopping-storage-service/src:/app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs 2>/dev/null || exit 1

ENTRYPOINT ["dumb-init", "--"]

CMD ["python3", "main.py"]