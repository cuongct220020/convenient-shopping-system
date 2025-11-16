import os
from dotenv import load_dotenv
from shopping_shared.configs import PostgreSQLConfig, RedisConfig, KafkaConfig

load_dotenv() # Load .env


class Config:
    """ Service-specific configurations for User-Service. """
    RUN_SETTING = {
        'host': os.getenv('APP_HOST', 'localhost'),
        'port': int(os.getenv('APP_PORT', '1337')),
        'debug': os.getenv('DEBUG', True).lower() == 'true',
        "access_log": False,
        "auto_reload": True,
        'workers': int(os.getenv('WORKERS', 1)),
    }

    # JWT Settings
    JWT_SECRET = os.getenv('JWT_SECRET', '85c145a16bd6f6e1f3e104ca78c6a102')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_MINUTES = os.getenv('JWT_EXPIRATION_MINUTES', 5)
    REFRESH_TOKEN_EXPIRE_DAYS = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7)

    # PostgreSQL Settings
    POSTGRESQL = PostgreSQLConfig(
        driver=os.getenv('POSTGRES_DB_DRIVER', 'postgresql+asyncpg'),
        user=os.getenv('POSTGRES_DB_USER', 'myname'),
        password=os.getenv('POSTGRES_DB_PASSWORD', 'mypassword'),
        host=os.getenv('POSTGRES_DB_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_DB_PORT', 5432)),
        name=os.getenv('POSTGRES_DB_NAME', 'convenient_shopping')
    )

    # Redis Setting
    REDIS = RedisConfig(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        password=os.getenv('REDIS_PASSWORD', 'mypassword'),
        decode_responses=os.getenv('REDIS_DECODE_RESPONSES', True)
    )

    # Kafka Setting
    KAFKA = KafkaConfig(
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    )







