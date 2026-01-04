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
    system_role: SystemRole = Field(SystemRole.USER, description="The system role of the user")
    is_active: bool = Field(True, description="Whether the user is active")


@openapi.component
class UserAdminViewSchema(UserDetailedProfileSchema):
    """Detailed user view for administrators."""
    system_role: SystemRole
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: datetime
    last_login: Optional[datetime] = None


@openapi.component
class UserAdminUpdateSchema(UserInfoUpdateSchema):
    """
    Schema for admins to update any user's information.
    Inherits core info update fields (username, email, names, phone, avatar).
    Adds admin-specific fields and nested profile updates.
    """
    system_role: Optional[SystemRole] = Field(None, description="The system role of the user")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    identity_profile: Optional[UserIdentityProfileUpdateSchema] = Field(None)
    health_profile: Optional[UserHealthProfileUpdateSchema] = Field(None)


@openapi.component
class PaginatedUserAdminViewResponseSchema(BaseSchema):
    """Schema for paginated response of family groups."""
    data: List[UserAdminViewSchema] = Field(default=[], description="List of users in")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")