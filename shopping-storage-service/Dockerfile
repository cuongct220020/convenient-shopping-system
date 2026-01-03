FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc git && \
    rm -rf /var/lib/apt/lists/*

COPY shared /app/shared
COPY shopping-storage-service /app/shopping-storage-service

WORKDIR /app/shopping-storage-service
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app/shopping-storage-service/src

EXPOSE 8002

CMD ["python", "main.py"]

