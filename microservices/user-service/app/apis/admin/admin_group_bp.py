from app.apis.admin import admin_bp
from app.views.admin.admin_group_view import (
    AdminGroupsView,
    AdminGroupDetailView,
    AdminGroupMembersView,
    AdminGroupMembersManageView
)

admin_bp.add_route(AdminGroupsView.as_view(), '/groups')
admin_bp.add_route(AdminGroupDetailView.as_view(), '/groups/<group_id:int>')
admin_bp.add_route(AdminGroupMembersView.as_view(), '/groups/<group_id:int>/members')