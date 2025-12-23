# microservices/user-service/app/apis/__init__.py
from sanic import Blueprint

from .auth_bp import auth_bp
from .group_bp import group_bp
from .user_bp import user_bp
from .admin_bp import admin_bp
from .user_tag_bp import user_tag_bp


api = Blueprint.group(
    group_bp,
    user_bp,
    admin_bp,
    auth_bp,
    user_tag_bp
)