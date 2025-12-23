# user-service/app/apis/group_bp.py
from sanic import Blueprint

from app.views.groups.group_view import (
    GroupView, 
    GroupMemberView, 
    MemberIdentityProfileView, 
    MemberHealthProfileView
)


group_bp = Blueprint('group_bp', url_prefix='/groups')

# /groups
group_bp.add_route(GroupView.as_view(), '/')
# /groups/{groupId}
group_bp.add_route(GroupView.as_view(), '/<group_id:uuid>')

# /groups/{groupId}/members
group_bp.add_route(GroupMemberView.as_view(), '/<group_id:uuid>/members')
# /groups/{groupId}/members/me (Allow member to leave group)
group_bp.add_route(GroupMemberView.as_view(), '/<group_id:uuid>/members/me')
# /groups/{groupId}/members/{userId}
group_bp.add_route(GroupMemberView.as_view(), '/<group_id:uuid>/members/<user_id:uuid>')

# Cross-member profile viewing
group_bp.add_route(MemberIdentityProfileView.as_view(), '/<group_id:uuid>/members/<user_id:uuid>/identity-profile')
group_bp.add_route(MemberHealthProfileView.as_view(), '/<group_id:uuid>/members/<user_id:uuid>/health-profile')