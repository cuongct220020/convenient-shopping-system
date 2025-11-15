# /microservices/user-service/app/schemas/auth.py
from typing import Optional

from pydantic import Field, EmailStr, SecretStr

from app.schemas.user import UserInfoSchema
from shopping_shared.schemas.base_schema import BaseSchema

# --- Authentication Schemas ---
class RegisterRequestSchema(BaseSchema):
    """Schema for user registration requests."""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: SecretStr
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)


class LoginRequestSchema(BaseSchema):
    """Schema for user login requests."""
    identifier: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Username or Email"
    )
    password: SecretStr

class LoginResponseSchema(BaseSchema):
    """Schema for user login responses."""
    access_token: str
    user_info: Optional[UserInfoSchema] = None


class AccessTokenSchema(BaseSchema):
    """Schema for token responses."""
    access_token: str
    token_type: str = "Bearer"
    expires_in_minutes: int


class ChangePasswordRequestSchema(BaseSchema):
    """Schema for an authenticated user to change their password."""
    current_password: SecretStr
    new_password: SecretStr
