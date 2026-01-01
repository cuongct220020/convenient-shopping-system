# app/apis/__init__.py
from sanic import Blueprint

# Import WebSocket Blueprint
from .ws_bp import ws_bp

# Tạo blueprint chính chứa tất cả các route
api = Blueprint.group(
    ws_bp,
    url_prefix="/ws"
)