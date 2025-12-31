# app/apis/__init__.py
from sanic import Blueprint

# Import WebSocket Blueprint
from .ws_bp import ws_bp

# Có thể thêm các API Blueprint khác sau này nếu cần
# from .notification_api_bp import notification_api_bp

# Tạo blueprint chính chứa tất cả các route
api = Blueprint.group(
    ws_bp,
    # notification_api_bp,  # Thêm sau nếu cần HTTP API
    url_prefix="/api/v1/notification-service"
)