# user-service/app/schemas/user_schema.py
from typing import Optional
from uuid import UUID
from pydantic import Field, EmailStr
from shopping_shared.schemas.base_schema import BaseSchema
from .otp_schema import OTPRequestSchema
from .user_profile_schema import UserIdentityProfileSchema, UserHealthProfileSchema


class UserInfoSchema(BaseSchema):
    """Publicly available user information."""
    id: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: Optional[str] = Field(None, validation_alias="phone_num")
    avatar_url: Optional[str] = None


class UserPublicProfileSchema(BaseSchema):
    """Public profile schema for general display (e.g. comments, group members)."""
    id: UUID
    username: str
    first_name: str
    last_name: str
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
    username: str = Field(..., max_length=255)
    email: EmailStr
    password_hash: str  # This will be the hashed password
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = False


class UserDetailedProfileSchema(UserInfoSchema):
    """Full user profile including identity and health info."""
    identity_profile: Optional[UserIdentityProfileSchema] = None
    health_profile: Optional[UserHealthProfileSchema] = None

