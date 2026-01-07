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
COPY user-service/requirements.prod.txt /app/user-service/requirements.txt
COPY shared /app/shared

# Install dependencies
RUN cp /app/user-service/requirements.txt /app/user-service/requirements_filtered.txt && \
    sed -i '/-e \.\.\/shared/d' /app/user-service/requirements_filtered.txt && \
    pip install --no-cache-dir /app/shared && \
    pip install --no-cache-dir -r /app/user-service/requirements_filtered.txt

# Stage 2: Runtime
FROM python:3.13-slim AS runtime

WORKDIR /app/user-service

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    dumb-init \
    curl \
    ca-certificates \
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
COPY --chown=appuser:appuser user-service/ /app/user-service/

# Set env
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Đảm bảo python tìm thấy path nếu cần thiết
    PYTHONPATH=/app/user-service

USER appuser

EXPOSE 9001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9001/api/v1/user-service/health || exit 1

ENTRYPOINT ["dumb-init", "--"]

# Khuyên dùng: Gọi qua python module để tránh lỗi path tuyệt đối
CMD ["python3", "run.py"]