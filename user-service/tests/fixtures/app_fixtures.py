import pytest
from app import create_app
from app.config import Config

# Cấu hình riêng cho môi trường Test (nếu cần)
class TestConfig(Config):
    # Sử dụng DB test riêng để tránh ảnh hưởng DB dev/prod
    # Nếu chạy local, bạn có thể override lại connection string ở đây
    # POSTGRES_DB_NAME = "shopping_user_service_test_db"
    
    # Dummy secret for testing
    JWT_SECRET = "test_secret_key_1234567890" 
    pass

@pytest.fixture(scope="session")
def test_app():
    """Khởi tạo Sanic App dùng cho toàn bộ phiên test."""
    app = create_app(TestConfig)
    return app

@pytest.fixture(scope="session")
def test_client(test_app):
    """Cung cấp Sanic Test Client để gọi API."""
    return test_app.asgi_client
