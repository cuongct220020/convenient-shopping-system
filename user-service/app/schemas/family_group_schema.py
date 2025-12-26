# user-service/app/schemas/family_group_schema.py
from typing import Optional, List
from uuid import UUID
from pydantic import Field, EmailStr
from shopping_shared.schemas.base_schema import BaseSchema
from app.enums import GroupRole
from .user_schema import UserInfoSchema, UserDetailedProfileSchema


# Family Group Schemas
class FamilyGroupCreateSchema(BaseSchema):
    """Schema for creating a new groups."""
    group_name: str = Field(..., min_length=1, max_length=255)
    group_avatar_url: Optional[str] = None


class FamilyGroupUpdateSchema(BaseSchema):
    """Schema for updating a group."""
    group_name: Optional[str] = Field(None, min_length=1, max_length=255)
    group_avatar_url: Optional[str] = None


# Group Membership Schemas
class GroupMembershipCreateSchema(BaseSchema):
    user_id: UUID
    group_id: UUID
    role: GroupRole = GroupRole.MEMBER
    added_by_user_id: Optional[UUID] = None


class GroupMembershipUpdateSchema(BaseSchema):
    role: Optional[GroupRole] = None


class AddMemberRequestSchema(BaseSchema):
    email: EmailStr


# Family Group Detailed Schemas
class GroupMembershipSchema(BaseSchema):
    """Schema representing a member within a groups (Basic Info)."""
    user: UserInfoSchema
    role: GroupRole


class GroupMembershipDetailedSchema(BaseSchema):
    """Schema representing a member with FULL profile details."""
    user: UserDetailedProfileSchema
    role: GroupRole


class FamilyGroupDetailedSchema(BaseSchema):
    """Detailed schema for a groups, including its members."""
    id: UUID
    group_name: str
    group_avatar_url: Optional[str] = None
    creator: Optional[UserInfoSchema] = None
    members: List[GroupMembershipSchema] = Field(default=[], alias="group_memberships")