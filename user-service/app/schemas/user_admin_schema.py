# user-service/app/schemas/user_admin_schema.py
from datetime import datetime
from typing import Optional, List

from pydantic import Field

from app.enums import SystemRole
from app.schemas.user_profile_schema import UserDetailedProfileSchema
from app.schemas.user_schema import UserInfoUpdateSchema, UserCreateSchema
from app.schemas.user_profile_schema import UserIdentityProfileUpdateSchema, UserHealthProfileUpdateSchema
from shopping_shared.schemas.base_schema import BaseSchema


class UserAdminCreateSchema(UserCreateSchema):
    """
    Schema for admins to create a new user.
    Inherits fields: username, email, password, first_name, last_name.
    Adds: system_role, is_active.
    """
    system_role: SystemRole = SystemRole.USER
    is_active: bool = True


class UserAdminViewSchema(UserDetailedProfileSchema):
    """Detailed user view for administrators."""
    system_role: SystemRole
    created_at: datetime
    last_login: Optional[datetime] = None


class UserAdminUpdateSchema(UserInfoUpdateSchema):
    """
    Schema for admins to update any user's information.
    Inherits core info update fields (username, email, names, phone, avatar).
    Adds admin-specific fields and nested profile updates.
    """
    system_role: Optional[SystemRole] = None
    is_active: Optional[bool] = None
    identity_profile: Optional[UserIdentityProfileUpdateSchema] = None
    health_profile: Optional[UserHealthProfileUpdateSchema] = None


class PaginatedUserAdminViewResponseSchema(BaseSchema):
    """Schema for paginated response of family groups."""
    data: List[UserAdminViewSchema] = Field(default=[], description="List of users in")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")