import os
import pytest
from app import create_app
from app.config import Config
from shopping_shared.configs import PostgreSQLConfig, RedisConfig, KafkaConfig

# Cấu hình riêng cho môi trường Test (nếu cần)
class TestConfig(Config):
    # Sử dụng DB test riêng để tránh ảnh hưởng DB dev/prod
    # Nếu chạy local, bạn có thể override lại connection string ở đây
    POSTGRESQL = PostgreSQLConfig(
        driver=os.getenv('POSTGRES_DB_DRIVER', 'postgresql+asyncpg'),
        user=os.getenv('POSTGRES_DB_USER', 'myname'),
        password=os.getenv('POSTGRES_DB_PASSWORD', 'mypassword'),
        host=os.getenv('POSTGRES_DB_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_DB_PORT', 5432)),
        name="shopping_user_service_test_db"  # Use test database
    )

    # Redis config for testing
    REDIS = RedisConfig(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        password=os.getenv('REDIS_PASSWORD', 'mypassword'),
        decode_responses=os.getenv('REDIS_DECODE_RESPONSES', True)
    )

    # Kafka config for testing
    KAFKA = KafkaConfig(
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9094')
    )

    # Dummy secret for testing
    JWT_SECRET = "test_secret_key_1234567890"

@pytest.fixture(scope="session")
def test_app():
    """Khởi tạo Sanic App dùng cho toàn bộ phiên test."""
    app = create_app(TestConfig)
    return app

@pytest.fixture(scope="session")
def test_client(test_app):
    """Cung cấp Sanic Test Client để gọi API."""
    return test_app.asgi_client
