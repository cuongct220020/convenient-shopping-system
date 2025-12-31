FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc git && \
    rm -rf /var/lib/apt/lists/*

COPY recipe-service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY recipe-service/ .

ENV PYTHONPATH=/app/src:$PYTHONPATH

EXPOSE 8001

CMD ["python", "main.py"]

