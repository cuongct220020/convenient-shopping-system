FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc git && \
    rm -rf /var/lib/apt/lists/*

COPY meal-service /app/meal-service

WORKDIR /app/meal-service
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app/meal-service/src:/app

EXPOSE 8003

CMD ["python", "main.py"]