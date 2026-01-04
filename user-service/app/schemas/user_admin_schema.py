# user-service/app/schemas/user_admin_schema.py
from datetime import datetime
from typing import Optional, List

from pydantic import Field
from sanic_ext.extensions.openapi import openapi

from app.enums import SystemRole
from app.schemas.user_profile_schema import UserDetailedProfileSchema
from app.schemas.user_schema import UserInfoUpdateSchema, UserCreateSchema
from app.schemas.user_profile_schema import UserIdentityProfileUpdateSchema, UserHealthProfileUpdateSchema
from shopping_shared.schemas.base_schema import BaseSchema

@openapi.component
class UserAdminCreateSchema(UserCreateSchema):
    """
    Schema for admins to create a new user.
    Inherits fields: username, email, password, first_name, last_name.
    Adds: system_role, is_active.
    """
    system_role: SystemRole = Field(
        SystemRole.USER,
        description="The system role of the user",
        examples=["admin", "user"]
    )
    is_active: bool = Field(
        True,
        description="Whether the user is active",
        examples=[True, False]
    )


@openapi.component
class UserAdminViewSchema(UserDetailedProfileSchema):
    """Detailed user view for administrators."""
    system_role: SystemRole = Field(
        ...,
        description="The system role of the user",
        examples=["admin", "user"]
    )
    is_active: bool = Field(
        ...,
        description="Whether the user is active",
        examples=[True, False]
    )
    created_at: datetime = Field(
        ...,
        description="The creation timestamp of the user",
        examples=["2023-01-01T00:00:00Z"]
    )
    last_login: Optional[datetime] = Field(
        None,
        description="The last login timestamp of the user",
        examples=["2023-01-01T00:00:00Z"]
    )


@openapi.component
class UserAdminUpdateSchema(UserInfoUpdateSchema):
    """
    Schema for admins to update any user's information.
    Inherits core info update fields (username, email, names, phone, avatar).
    Adds admin-specific fields and nested profile updates.
    """
    system_role: Optional[SystemRole] = Field(
        None,
        description="The system role of the user",
        examples=["admin", "user"]
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the user is active",
        examples=[True, False]
    )
    identity_profile: Optional[UserIdentityProfileUpdateSchema] = Field(
        None,
        description="Identity profile updates for the user"
    )
    health_profile: Optional[UserHealthProfileUpdateSchema] = Field(
        None,
        description="Health profile updates for the user"
    )


@openapi.component
class PaginatedUserAdminViewResponseSchema(BaseSchema):
    """Schema for paginated response of family groups."""
    data: List[UserAdminViewSchema] = Field(
        default=[],
        description="List of users in",
        examples=[[{
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "admin_user",
            "email": "admin@example.com",
            "system_role": "admin",
            "is_active": True,
            "created_at": "2023-01-01T00:00:00Z"
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