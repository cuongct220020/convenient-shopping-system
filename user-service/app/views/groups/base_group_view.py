# user-service/app/views/groups/base_group_view.py
from sanic import Request

from app.repositories.user_repository import UserRepository
from app.repositories.family_group_repository import FamilyGroupRepository
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.services.family_group_service import FamilyGroupService
from app.views.base_view import BaseAPIView

class BaseGroupView(BaseAPIView):
    """Base view with helper to get FamilyGroupService."""

    @staticmethod
    def _get_service(request: Request) -> FamilyGroupService:
        session=request.ctx.db_session
        group_repo = FamilyGroupRepository(session=session)
        member_repo = GroupMembershipRepository(session=session)
        user_repo = UserRepository(session=session)
        return FamilyGroupService(group_repo, member_repo, user_repo)