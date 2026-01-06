# ===== BUILD STAGE =====
FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends gcc git && \
    rm -rf /var/lib/apt/lists/*

COPY recipe-service/requirements.txt /build/requirements.txt

RUN head -n -1 requirements.txt > requirements-docker.txt

RUN pip install --upgrade pip wheel
RUN pip wheel -w /build/wheels -r requirements-docker.txt


# ===== RUN STAGE =====
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY shared /app/shared
COPY recipe-service /app/recipe-service

RUN pip install --no-cache-dir -e /app/shared[fastapi]

ENV PYTHONPATH=/app/recipe-service/src:/app

WORKDIR /app/recipe-service

EXPOSE 9002

CMD ["python", "main.py"]