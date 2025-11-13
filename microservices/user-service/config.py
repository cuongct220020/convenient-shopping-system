import os
from dotenv import load_dotenv
from shopping_shared.configs import PostgreSQLConfig, RedisConfig, KafkaConfig

load_dotenv() # Load .env

# Default configuration for service-specific settings
DEFAULT_APP_HOST = 'localhost'
DEFAULT_APP_PORT = 1337
DEFAULT_DEBUG_MODE = True
DEFAULT_WORKER_COUNT = 2

DEFAULT_JWT_SECRET = '85c145a16bd6f6e1f3e104ca78c6a102'
DEFAULT_JWT_ALGORITHM = 'HS256'
DEFAULT_JWT_EXPIRATION_MINUTES = 10
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = 7

class Config:
    """ Service-specific configurations for User-Service. """
    RUN_SETTING = {
        'host': os.getenv('APP_HOST', DEFAULT_APP_HOST),
        'port': int(os.getenv('APP_PORT', DEFAULT_APP_PORT)),
        'debug': os.getenv('DEBUG', DEFAULT_DEBUG_MODE).lower() == 'true',
        "access_log": False,
        "auto_reload": True,
        'workers': int(os.getenv('WORKERS', DEFAULT_WORKER_COUNT)),
    }

    JWT_SECRET = os.getenv('JWT_SECRET', DEFAULT_JWT_SECRET)
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', DEFAULT_JWT_ALGORITHM)
    JWT_EXPIRATION_MINUTES = os.getenv('JWT_EXPIRATION_MINUTES', DEFAULT_JWT_EXPIRATION_MINUTES)
    REFRESH_TOKEN_EXPIRE_DAYS = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS)

