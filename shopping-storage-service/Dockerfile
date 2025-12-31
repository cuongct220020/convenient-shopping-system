FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc git && \
    rm -rf /var/lib/apt/lists/*

COPY shopping-storage-service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY shopping-storage-service/ .

ENV PYTHONPATH=/app/src:$PYTHONPATH

EXPOSE 8002

CMD ["python", "main.py"]

