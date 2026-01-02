FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc git && \
    rm -rf /var/lib/apt/lists/*

COPY shared /app/shared
COPY recipe-service /app/recipe-service

RUN pip install --no-cache-dir -v -e /app/shared[fastapi]

WORKDIR /app/recipe-service
RUN head -n -1 requirements.txt > requirements-docker.txt
RUN cat requirements-docker.txt
RUN pip install --no-cache-dir -v -r requirements-docker.txt

ENV PYTHONPATH=/app/recipe-service/src:/app

EXPOSE 8001

CMD ["python", "main.py"]