# microservices/user-service/app/apis/admin/__init__.py

from sanic import Blueprint

admin_bp = Blueprint('Admin', url_prefix='/admin')
