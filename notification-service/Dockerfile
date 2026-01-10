# Stage 1: Dependencies Builder
FROM python:3.13-slim AS dependencies-builder

WORKDIR /app
# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    zlib1g-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements
COPY notification-service/requirements.prod.txt /app/notification-service/requirements.txt
COPY shared /app/shared

# Install dependencies
RUN cp /app/notification-service/requirements.txt /app/notification-service/requirements_filtered.txt && \
    sed -i '/-e \.\.\/shared/d' /app/notification-service/requirements_filtered.txt && \
    pip install --no-cache-dir /app/shared && \
    pip install --no-cache-dir -r /app/notification-service/requirements_filtered.txt

# Stage 2: Runtime
FROM python:3.13-slim AS runtime

WORKDIR /app/notification-service

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


# Copy site-packages (Thư viện code)
COPY --from=dependencies-builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
# Copy binaries (File chạy lệnh: alembic, sanic, gunicorn...)
COPY --from=dependencies-builder /usr/local/bin /usr/local/bin
# ------------------------

# Copy application code
COPY --chown=appuser:appuser notification-service/ /app/notification-service/

# Set env
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Đảm bảo python tìm thấy path nếu cần thiết
    PYTHONPATH=/app/notification-service

USER appuser

EXPOSE 9005

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9005/api/v1/notification-service/health || exit 1

ENTRYPOINT ["dumb-init", "--"]

CMD ["python3", "run.py"]