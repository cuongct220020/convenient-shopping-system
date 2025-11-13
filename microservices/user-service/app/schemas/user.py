# /microservices/user-service/app/schemas/user.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import Field, EmailStr
from shopping_shared.schemas.base_schema import BaseSchema
from app.constants import UserRole
from .profile import UserIdentityProfileSchema, UserHealthProfileSchema, UserIdentityProfileUpdateSchema, UserHealthProfileUpdateSchema

# --- Base User Schemas ---
class UserPublicProfileSchema(BaseSchema):
    """Publicly available user information."""
    id: UUID
    user_name: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None

class UserCoreInfoSchema(UserPublicProfileSchema):
    """Core user information for the authenticated user."""
    email: EmailStr
    phone_num: Optional[str] = None

class UserUpdateSchema(BaseSchema):
    """Schema for updating basic user info."""
    phone_num: Optional[str] = Field(None, max_length=20)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None

# --- Detailed and Admin Schemas ---
class UserDetailedProfileSchema(UserCoreInfoSchema):
    """Full user profile including identity and health info."""
    identity_profile: Optional[UserIdentityProfileSchema] = None
    health_profile: Optional[UserHealthProfileSchema] = None

class UserAdminViewSchema(UserDetailedProfileSchema):
    """Detailed user view for administrators."""
    system_role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None

class UserAdminUpdateSchema(UserUpdateSchema):
    """Schema for admins to update any user's information."""
    user_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    system_role: Optional[UserRole] = None
    identity_profile: Optional[UserIdentityProfileUpdateSchema] = None
    health_profile: Optional[UserHealthProfileUpdateSchema] = None
