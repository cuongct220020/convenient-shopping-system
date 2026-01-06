# user-service/app/schemas/family_group_schema.py
from typing import Optional, List
from uuid import UUID
from pydantic import Field
from sanic_ext import openapi
from shopping_shared.schemas.base_schema import BaseSchema
from app.enums import GroupRole
from app.schemas.user_schema import UserCoreInfoSchema
from app.schemas.user_profile_schema import UserDetailedProfileSchema


# Family Group Schemas
@openapi.component
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

@openapi.component
class FamilyGroupUpdateSchema(BaseSchema):
    """Schema for updating a group."""
    group_name: Optional[str] = Field(
        None,
        description="The name of the new family group",
        examples=["updated_group_name"],
        min_length=1,
        max_length=255
    )
    group_avatar_url: Optional[str] = Field(
        None,
        description="The url to the avatar of the new family group",
        examples=["https://example.com/avatar.jpg"]
    )


# Group Membership Schemas
@openapi.component
class GroupMembershipCreateSchema(BaseSchema):
    user_id: UUID = Field(
        ...,
        description="The ID of the user",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    group_id: UUID = Field(
        ...,
        description="The ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174001"]
    )
    role: GroupRole = Field(
        GroupRole.MEMBER,
        description="The role of the user",
        examples=["member", "head_chef"]
    )
    added_by_user_id: Optional[UUID] = Field(
        None,
        description="The ID of the user",
        examples=["123e4567-e89b-12d3-a456-426614174002"]
    )


@openapi.component
class GroupMembershipUpdateSchema(BaseSchema):
    role: Optional[GroupRole] = Field(
        None,
        description="The role of the user",
        examples=["member", "head_chef"]
    )


@openapi.component
class AddMemberRequestSchema(BaseSchema):
    identifier: str = Field(
        ...,
        description="Username or Email address of the user",
        examples=["cuongct", "cuongct@example.com"],
        min_length=3,
        max_length=255,
    )


# Family Group Detailed Schemas
@openapi.component
class GroupMembershipSchema(BaseSchema):
    """Schema representing a member within a groups (Basic Info)."""
    user: UserCoreInfoSchema
    role: GroupRole = Field(
        ...,
        description="The role of the user in the group",
        examples=["member", "head_chef"]
    )


@openapi.component
class GroupMembershipDetailedSchema(BaseSchema):
    """Schema representing a member with FULL profile details."""
    user: UserDetailedProfileSchema
    role: GroupRole = Field(
        ...,
        description="The role of the user in the group",
        examples=["member", "head_chef"]
    )


@openapi.component
class FamilyGroupDetailedSchema(BaseSchema):
    """Detailed schema for a groups, including its members."""
    id: UUID = Field(
        ...,
        description="The unique identifier of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    group_name: str = Field(
        ...,
        description="The name of the group",
        examples=["My Family Group"]
    )
    group_avatar_url: Optional[str] = Field(
        None,
        description="The URL to the group's avatar",
        examples=["https://example.com/group-avatar.jpg"]
    )
    creator: Optional[UserCoreInfoSchema] = None
    members: List[GroupMembershipSchema] = Field(
        default=[],
        description="List of members in the group",
        alias="group_memberships"
    )


@openapi.component
class UserGroupSchema(BaseSchema):
    """Schema for a group when listing user's groups, including the user's role in that group."""
    id: UUID = Field(
        ...,
        description="The unique identifier of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    group_name: str = Field(
        ...,
        description="The name of the group",
        examples=["My Family Group"]
    )
    group_avatar_url: Optional[str] = Field(
        None,
        description="The URL to the group's avatar",
        examples=["https://example.com/group-avatar.jpg"]
    )
    creator: Optional[UserCoreInfoSchema] = None
    role_in_group: GroupRole = Field(
        ...,
        description="The role of the current user in this group",
        examples=["member", "head_chef"]
    )
    member_count: int = Field(
        default=0,
        description="Number of members in the group",
        examples=[3, 5]
    )


@openapi.component
class UserGroupListResponseSchema(BaseSchema):
    """Schema for the response when listing user's groups."""
    groups: List[UserGroupSchema] = Field(
        default=[],
        description="List of groups the user is a member of",
        examples=[[{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "group_name": "My Family Group",
            "group_avatar_url": "https://example.com/group-avatar.jpg",
            "role_in_group": "member",
            "member_count": 3
        }]]
    )


@openapi.component
class PaginatedFamilyGroupsResponseSchema(BaseSchema):
    """Schema for paginated response of family groups."""
    data: List[FamilyGroupDetailedSchema] = Field(
        default=[],
        description="List of family groups",
        examples=[[{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "group_name": "My Family Group",
            "group_avatar_url": "https://example.com/group-avatar.jpg",
            "members": []
        }]]
    )
    page: int = Field(
        ...,
        description="Current page number",
        examples=[1]
    )
    page_size: int = Field(
        ...,
        description="Number of items per page",
        examples=[10]
    )
    total_items: int = Field(
        ...,
        description="Total number of items",
        examples=[25]
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages",
        examples=[3]
    )