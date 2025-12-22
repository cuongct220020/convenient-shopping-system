# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and source code
COPY requirements.txt ./
COPY src/ ./src/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (adjust if needed)
EXPOSE 9996

# Run the service (adjust entrypoint if needed)
CMD ["python", "src/main.py"]