# app/apis/__init__.py
from sanic import Blueprint

# Import Blueprints
from .ws_bp import ws_bp
from .notification_bp import notification_bp

# Tạo blueprint chính chứa tất cả các route
api = Blueprint.group(
    ws_bp,
    notification_bp,
    url_prefix="/ws"
)