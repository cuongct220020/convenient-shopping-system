# app/apis/admin_user_bp.py
from app.apis.admin import admin_bp
from app.views.admin.admin_user_view import AdminUsersView, AdminUserDetailView

# Routes for Admin User Management
admin_bp.add_route(AdminUsersView.as_view(), '/users')
admin_bp.add_route(AdminUserDetailView.as_view(), '/users/<user_id:int>')