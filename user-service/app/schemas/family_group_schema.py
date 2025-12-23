# user-service/app/schemas/groups.py
from typing import Optional, List
from uuid import UUID
from pydantic import Field
from shopping_shared.schemas.base_schema import BaseSchema
from app.enums import GroupRole
from .user_schema import UserInfoSchema



class FamilyGroupCreateSchema(BaseSchema):
    """Schema for creating a new groups."""
    group_name: str = Field(..., min_length=1, max_length=255)
    group_avatar_url: Optional[str] = None



class FamilyGroupUpdateSchema(BaseSchema):
    """Schema for updating a group."""
    group_name: Optional[str] = Field(None, min_length=1, max_length=255)
    group_avatar_url: Optional[str] = None



class GroupMembershipSchema(BaseSchema):
    """Schema representing a member within a groups."""
    user: UserInfoSchema
    role: GroupRole


class GroupMembershipCreateSchema(BaseSchema):
    user_id: UUID
    role: GroupRole = GroupRole.MEMBER


class GroupMembershipUpdateSchema(BaseSchema):



class FamilyGroupDetailedSchema(BaseSchema):
    """Detailed schema for a groups, including its members."""
    id: UUID
    group_name: str
    group_avatar_url: Optional[str] = None
    creator: Optional[UserInfoSchema] = None
    members: List[FamilyGroupMemberSchema] = []
