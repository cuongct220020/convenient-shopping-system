# /microservices/user-service/app/schemas/user.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import Field, EmailStr
from shopping_shared.schemas.base_schema import BaseSchema
from app.constants import UserRole
from .user_profile import UserIdentityProfileSchema, UserHealthProfileSchema, UserIdentityProfileUpdateSchema, UserHealthProfileUpdateSchema

# --- Base User Schemas ---
class UserInfoSchema(BaseSchema):
    """Publicly available user information."""
    id: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None


class UserInfoUpdateSchema(BaseSchema):
    """Schema for update user core information."""
    username: Optional[str] = None
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone_num: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreateSchema(BaseSchema):
    """Schema for creating a new user, used internally."""
    user_name: str = Field(..., max_length=255)
    email: EmailStr
    password: str  # This will be the hashed password
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = False


class UserAdminCreateSchema(UserCreateSchema):
    """Schema for admins to create a new user."""
    system_role: UserRole = UserRole.USER


# --- Detailed and Admin Schemas ---
class UserDetailedProfileSchema(UserInfoSchema):
    """Full user profile including identity and health info."""
    identity_profile: Optional[UserIdentityProfileSchema] = None
    health_profile: Optional[UserHealthProfileSchema] = None


class UserAdminViewSchema(UserDetailedProfileSchema):
    """Detailed user view for administrators."""
    system_role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None


class UserAdminUpdateSchema(UserInfoUpdateSchema):
    """Schema for admins to update any user's information."""
    system_role: Optional[UserRole] = None
    identity_profile: Optional[UserIdentityProfileUpdateSchema] = None
    health_profile: Optional[UserHealthProfileUpdateSchema] = None
