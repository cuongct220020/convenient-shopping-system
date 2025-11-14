# app/apis/user_admin_bp.py
from sanic import Blueprint
from app.views.admin.admin_user_view import AdminUserListView, AdminUserDetailView

# All routes in this blueprint will be prefixed with /api/v1/admin
admin_bp = Blueprint('Admin', url_prefix='/admin')

# Routes for Admin User Management
admin_bp.add_route(AdminUserListView.as_view(), '/users')
admin_bp.add_route(AdminUserDetailView.as_view(), '/users/<user_id:int>')