FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc git && \
    rm -rf /var/lib/apt/lists/*

COPY meal-service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY meal-service/ .

ENV PYTHONPATH=/app/src:$PYTHONPATH

EXPOSE 8003

CMD ["python", "main.py"]

