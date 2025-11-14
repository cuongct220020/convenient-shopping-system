from sanic import Blueprint

from .auth_bp import auth_bp
from .group_bp import group_bp
from .user_bp import user_bp
from .admin import admin_bp

api = Blueprint.group(
    auth_bp,
    group_bp,
    user_bp,
    admin_bp
)