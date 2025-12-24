# user-service/app/schemas/user_admin_schema.py
from datetime import datetime
from typing import Optional
from app.enums import SystemRole
from app.schemas.auth_schema import RegisterRequestSchema
from app.schemas.user_schema import UserDetailedProfileSchema, UserInfoUpdateSchema
from app.schemas.user_profile_schema import UserIdentityProfileUpdateSchema, UserHealthProfileUpdateSchema


class UserAdminCreateSchema(RegisterRequestSchema):
    """
    Schema for admins to create a new user.
    Inherits fields: username, email, password, first_name, last_name.
    Adds: system_role, is_active.
    """
    system_role: SystemRole = SystemRole.USER
    is_active: bool = True
    phone_num: Optional[str] = None


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