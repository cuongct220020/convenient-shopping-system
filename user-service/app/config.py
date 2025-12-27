import os
from pathlib import Path

from dotenv import load_dotenv
from shopping_shared.configs import PostgreSQLConfig, RedisConfig, KafkaConfig

# Explicitly load .env from user-service directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """ Service-specific configurations for User-Service. """
    # Proxy Configuration (Sanic v22+)
    PROXIES_COUNT = 1
    PROXIES_OR_NETWORKS = "*" 

    RUN_SETTING = {
        'host': os.getenv('APP_HOST', 'localhost'),
        'port': int(os.getenv('APP_PORT', '8000')),
        'debug': os.getenv('DEBUG', True).lower() == 'true',
        "access_log": False,
        "auto_reload": True,
        'workers': int(os.getenv('WORKERS', 1)),
    }

    # JWT Settings
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'RS256')
    JWT_ISSUER = os.getenv('JWT_ISSUER', 'shopping-user-service')  # Must match Kong's 'iss'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 15))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))

    # Load RSA keys
    @staticmethod
    def _load_rsa_key(env_path_key: str, required: bool = False) -> str:
        """Load RSA key from env variable or file path."""
        key_path = os.getenv(env_path_key)
        
        if not key_path:
            if required:
                raise ValueError(f"CRITICAL: Missing {env_path_key} in environment variables.")
            return None

        path = Path(key_path)
        if not path.is_absolute():
            # Resolve relative to project root (user-service/)
            base_dir = Path(__file__).resolve().parent.parent
            path = base_dir / path

        if not path.exists():
            if required:
                raise FileNotFoundError(f"CRITICAL: RSA key file not found at: {path}")
            return None

        return path.read_text()

    # For RS256
    _is_asymmetric = JWT_ALGORITHM.startswith('RS')
    JWT_PRIVATE_KEY = _load_rsa_key.__func__(
        'JWT_PRIVATE_KEY_PATH', required=_is_asymmetric
    )
    JWT_PUBLIC_KEY = _load_rsa_key.__func__(
        'JWT_PUBLIC_KEY_PATH', required=_is_asymmetric
    )

    # For HS256 (fallback)
    # JWT_SECRET = os.getenv('JWT_SECRET', 'e3dc8799821e1035ff0decd11ee02750f4740783b620e5f9c1c92020056ec10e')


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



