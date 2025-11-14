# microservices/user-service/app/apis/group_bp.py
from sanic import Blueprint

from app.views.groups.group_view import GroupView, GroupMemberView


group_bp = Blueprint('group_bp', url_prefix='/groups')

group_bp.add_route(GroupView.as_view(), '/')

group_bp.add_route(GroupMemberView.as_view(), '/groups/<group_id>')