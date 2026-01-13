import os
from pathlib import Path

from dotenv import load_dotenv
from shopping_shared.configs import PostgreSQLConfig, RedisConfig, KafkaConfig

# Explicitly load .env from notification-service directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """ Service-specific configurations for Notification-Service. """

    RUN_SETTING = {
        'host': os.getenv('APP_HOST', 'localhost'),
        'port': int(os.getenv('APP_PORT', '8000')),
        'debug': os.getenv('DEBUG', True).lower() == 'true',
        "access_log": True,
        "auto_reload": True,
        'workers': int(os.getenv('WORKERS', 1)),
    }


    # PostgreSQL Settings
    POSTGRESQL = PostgreSQLConfig(
        driver=os.getenv('POSTGRES_DB_DRIVER', 'postgresql+asyncpg'),
        user=os.getenv('POSTGRES_DB_USER', 'myname'),
        password=os.getenv('POSTGRES_DB_PASSWORD', 'mypassword'),
        host=os.getenv('POSTGRES_DB_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_DB_PORT', 5432)),
        name=os.getenv('POSTGRES_DB_NAME', 'shopping_notification_service_db')
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

    # Email Settings
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 1025))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'false').lower() == 'true'
    EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'noreply@example.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'dummy')

    # User Service URL (internal container URL)
    USER_SERVICE_URL: str = os.getenv('USER_SERVICE_URL', 'http://user-service:8000')

    # # OpenAPI / Swagger Configuration
    # OAS_URL_PREFIX = "/api/v2/notification-service/docs"
    # SWAGGER_UI_CONFIGURATION = {
    #     "docExpansion": "list",  # Expand only the endpoint list, not the full details
    #     "filter": True,  # Enable search/filter functionality
    #     "syntaxHighlight": {
    #         "theme": "monokai"  # Better syntax highlighting theme
    #     },
    #     "tryItOutEnabled": True,  # Always show "Try it out" button
    #     "displayRequestDuration": True,  # Show API response time
    #     "defaultModelsExpandDepth": -1,  # Hide schemas section to reduce clutter
    # }
    # OAS = {
    #     "info": {
    #         "title": "Convenient Shopping System - Notification Service API",
    #         "version": "1.0.0",
    #         "description": "API quản lý thông báo thời gian thực cho hệ thống mua sắm tiện lợi.",
    #         "contact": {
    #             "email": "cuongct0902@example.com",
    #         },
    #     },
    #     "servers": [
    #         {"url": "http://localhost:8000", "description": "Local Kong Gateway"},
    #         {"url": "http://localhost:9005", "description": "Local Notification Service Direct"}
    #     ],
    #     "components": {
    #         "securitySchemes": {
    #             "BearerAuth": {
    #                 "type": "http",
    #                 "scheme": "bearer",
    #                 "bearerFormat": "JWT",
    #                 "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
    #             }
    #         }
    #     },
    #     "security": [{"BearerAuth": []}]
    # }