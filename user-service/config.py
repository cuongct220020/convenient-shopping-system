import os
from pathlib import Path

from dotenv import load_dotenv
from shopping_shared.configs import PostgreSQLConfig, RedisConfig, KafkaConfig

load_dotenv() # Load .env


class Config:
    """ Service-specific configurations for User-Service. """
    RUN_SETTING = {
        'host': os.getenv('APP_HOST', 'localhost'),
        'port': int(os.getenv('APP_PORT', '8000')),
        'debug': os.getenv('DEBUG', True).lower() == 'true',
        "access_log": False,
        "auto_reload": True,
        'workers': int(os.getenv('WORKERS', 1)),
        'proxies_count': 1, # Thêm để tin tưởng header từ Gateway
        'forwarded_for_header': 'x-forwarded-for',
    }

    # JWT Settings
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_MINUTES = os.getenv('JWT_EXPIRATION_MINUTES', 5)
    REFRESH_TOKEN_EXPIRE_DAYS = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7)

    # Load RSA keys
    @staticmethod
    def _load_rsa_key(env_key: str, env_path_key: str) -> str:
        """Load RSA key from env variable or file path."""
        # Try inline key first
        key = os.getenv(env_key)
        if key:
            return key.replace('\\n', '\n')  # Handle escaped newlines

        # Try file path
        key_path = os.getenv(env_path_key)
        if key_path:
            return Path(key_path).read_text()

        raise ValueError(f"Missing {env_key} or {env_path_key} in environment")

    # For RS256
    JWT_PRIVATE_KEY = _load_rsa_key.__func__(
        'JWT_PRIVATE_KEY',
        'JWT_PRIVATE_KEY_PATH'
    ) if os.getenv('JWT_ALGORITHM', 'RS256').startswith('RS') else None

    JWT_PUBLIC_KEY = _load_rsa_key.__func__(
        'JWT_PUBLIC_KEY',
        'JWT_PUBLIC_KEY_PATH'
    ) if os.getenv('JWT_ALGORITHM', 'RS256').startswith('RS') else None

    # For HS256 (fallback)
    JWT_SECRET = os.getenv('JWT_SECRET', 'e3dc8799821e1035ff0decd11ee02750f4740783b620e5f9c1c92020056ec10e')


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
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9094')
    )



