# user-service/app/apis/group_bp.py
from sanic import Blueprint

from app.views.groups import (
    GroupView,
    GroupDetailView,
    GroupMembersView,
    GroupMemberDetailView,
    GroupMemberMeView,
    MemberIdentityProfileView,
    MemberHealthProfileView,
    GroupAccessCheckView
)


group_bp = Blueprint('group_bp', url_prefix='/groups')
group_internal_bp = Blueprint('group_internal_bp', url_prefix='/groups/internal')

# /groups (POST: create group)
group_bp.add_route(GroupView.as_view(), '/', name='groups')

# /groups/{group_id} (GET, DELETE: view/delete group)
group_bp.add_route(GroupDetailView.as_view(), '/<group_id:uuid>', name='group_detail')

# /groups/{group_id}/members (GET, POST: list/add members)
group_bp.add_route(GroupMembersView.as_view(), '/<group_id:uuid>/members', name='group_members')

# /groups/{group_id}/members/me (DELETE: leave group)
group_bp.add_route(GroupMemberMeView.as_view(), '/<group_id:uuid>/members/me', name='group_member_me')

# /groups/{group_id}/members/{user_id} (PATCH, DELETE: update/remove member)
group_bp.add_route(GroupMemberDetailView.as_view(), '/<group_id:uuid>/members/<user_id:uuid>', name='group_member_detail')

# Cross-member profile viewing
group_bp.add_route(MemberIdentityProfileView.as_view(), '/<group_id:uuid>/members/<user_id:uuid>/identity-profile', name='member_identity_profile')
group_bp.add_route(MemberHealthProfileView.as_view(), '/<group_id:uuid>/members/<user_id:uuid>/health-profile', name='member_health_profile')

# Internal group access check
group_internal_bp.add_route(GroupAccessCheckView.as_view(), '/<group_id:uuid>/members/<user_id:uuid>/access-check', name='group_access_check')