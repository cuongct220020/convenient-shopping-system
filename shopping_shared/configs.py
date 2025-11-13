# shopping_shared/configs.py
import os
from dotenv import load_dotenv

# It's good practice to load .env file here so that any service using
# these configs will have its environment variables loaded.
load_dotenv()

class PostgreSQLConfig:
    """PostgreSQL database configuration."""
    DB_DRIVER = os.getenv('DB_DRIVER', 'postgresql+asyncpg')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DATABASE_URI = f'{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}' if all([DB_DRIVER, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]) else None

class RedisConfig:
    """Redis configuration."""
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

class KafkaConfig:
    """Kafka configuration."""
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

class EmailConfig:
    """Email server configuration (for Gmail)."""
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587  # Port for TLS
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
