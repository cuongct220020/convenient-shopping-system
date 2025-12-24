# user-service/app/apis/admin/admin_bp.py
from sanic import Blueprint

from app.views.admin.admin_group_view import (
    AdminGroupsView,
    AdminGroupDetailView,
    AdminGroupMembersView,
    AdminGroupMembersManageView
)
from app.views.admin.admin_user_view import AdminUsersView, AdminUserDetailView

admin_bp = Blueprint('admin_bp', url_prefix='/admin')

# Admin Group Management Routes
admin_bp.add_route(AdminGroupsView.as_view(), '/groups')
admin_bp.add_route(AdminGroupDetailView.as_view(), '/groups/<group_id:uuid>')
admin_bp.add_route(AdminGroupMembersView.as_view(), '/groups/<group_id:uuid>/members')
admin_bp.add_route(AdminGroupMembersManageView.as_view(), '/groups/<group_id:uuid>/members/<user_id:uuid>')

# Admin User Management Routes
admin_bp.add_route(AdminUsersView.as_view(), '/users')
admin_bp.add_route(AdminUserDetailView.as_view(), '/users/<user_id:uuid>')