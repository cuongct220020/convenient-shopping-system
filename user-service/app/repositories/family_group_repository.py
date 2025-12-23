# user-service/repositories/family_group_repository.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FamilyGroup, GroupMembership
from app.schemas import FamilyGroupCreateSchema, FamilyGroupUpdateSchema
from shopping_shared.databases.base_repository import BaseRepository


class FamilyGroupRepository(
    BaseRepository[
        FamilyGroup,
        FamilyGroupCreateSchema,
        FamilyGroupUpdateSchema
    ]
):
    def __init__(self, session: AsyncSession):
        super.__init__(FamilyGroup, session)




class GroupMembershipRepository(
    BaseRepository[
        GroupMembership,
        GroupMembershipCreateSchema,
        GroupMembershipUpdateSchema
    ]
):
    def __init__(self, session: AsyncSession):
        super.__init__(GroupMembership, session)

