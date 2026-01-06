# ===== BUILD STAGE =====
FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends gcc git && \
    rm -rf /var/lib/apt/lists/*

COPY meal-service/requirements.txt /build/requirements.txt

RUN pip install --upgrade pip wheel
RUN pip wheel -w /build/wheels -r requirements.txt


# ===== RUN STAGE =====
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY meal-service /app/meal-service

ENV PYTHONPATH=/app/meal-service/src

WORKDIR /app/meal-service

EXPOSE 9003

CMD ["python", "main.py"]