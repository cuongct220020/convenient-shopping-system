# app/apis/__init__.py
from sanic import Blueprint

# Import Blueprints
from .ws_bp import ws_bp
from .notification_bp import notification_bp

# REST APIs: expose directly (no extra prefix)
api = Blueprint.group(
    notification_bp,
)

# WebSocket APIs: expose under /ws/*
ws_api = Blueprint.group(
    ws_bp,
    url_prefix="/ws"
)