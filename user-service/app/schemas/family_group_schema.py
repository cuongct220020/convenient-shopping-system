# user-service/app/schemas/family_group_schema.py
from typing import Optional, List
from uuid import UUID
from pydantic import Field
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
    identifier: str = Field(
        ...,
        description="Username or Email address of the user",
        examples=["cuongct", "cuongct@example.com"],
        min_length=3,
        max_length=255,
    )


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


class UserGroupSchema(BaseSchema):
    """Schema for a group when listing user's groups, including the user's role in that group."""
    id: UUID
    group_name: str
    group_avatar_url: Optional[str] = None
    creator: Optional[UserCoreInfoSchema] = None
    role_in_group: GroupRole  # The role of the current user in this group
    member_count: int = Field(default=0, description="Number of members in the group")


class UserGroupListResponseSchema(BaseSchema):
    """Schema for the response when listing user's groups."""
    groups: List[UserGroupSchema] = Field(default=[], description="List of groups the user is a member of")


class PaginatedFamilyGroupsResponseSchema(BaseSchema):
    """Schema for paginated response of family groups."""
    data: List[FamilyGroupDetailedSchema] = Field(default=[], description="List of family groups")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")