FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc git && \
    rm -rf /var/lib/apt/lists/*

COPY shared /app/shared
COPY recipe-service /app/recipe-service

WORKDIR /app/recipe-service
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app/recipe-service/src

EXPOSE 8001

CMD ["python", "main.py"]