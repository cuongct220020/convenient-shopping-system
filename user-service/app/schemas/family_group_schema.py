# user-service/app/schemas/family_group_schema.py
from typing import Optional, List
from uuid import UUID
from pydantic import Field, EmailStr
from shopping_shared.schemas.base_schema import BaseSchema
from app.enums import GroupRole
from app.schemas.user_schema import UserCoreInfoSchema
from app.schemas.user_profile_schema import UserDetailedProfileSchema


# Family Group Schemas
class FamilyGroupCreateSchema(BaseSchema):
    """Schema for creating a new groups."""
    group_name: str = Field(
        ...,
        description="The name of the new family group",
        examples=["group1"],
        min_length=3,
        max_length=255
    )
    group_avatar_url: Optional[str] = Field(
        None,
        description="The url to the avatar of the new family group"
    )


class FamilyGroupUpdateSchema(BaseSchema):
    """Schema for updating a group."""
    group_name: Optional[str] = Field(
        None,
        description="The name of the new family group",
        examples=["group1"],
        min_length=1,
        max_length=255
    )
    group_avatar_url: Optional[str] = Field(
        None,
        description="The url to the avatar of the new family group"
    )


# Group Membership Schemas
class GroupMembershipCreateSchema(BaseSchema):
    user_id: UUID = Field(..., description="The ID of the user")
    group_id: UUID = Field(..., description="The ID of the group")
    role: GroupRole = Field(
        GroupRole.MEMBER,
        description="The role of the user"
    )
    added_by_user_id: Optional[UUID] = Field(None, description="The ID of the user")


class GroupMembershipUpdateSchema(BaseSchema):
    role: Optional[GroupRole] = None


class AddMemberRequestSchema(BaseSchema):
    email: EmailStr


# Family Group Detailed Schemas
class GroupMembershipSchema(BaseSchema):
    """Schema representing a member within a groups (Basic Info)."""
    user: UserCoreInfoSchema
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
    creator: Optional[UserCoreInfoSchema] = None
    members: List[GroupMembershipSchema] = Field(default=[], alias="group_memberships")