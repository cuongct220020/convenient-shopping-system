# user-service/app/schemas/auth_schema.py
from typing import Optional

from pydantic import Field, EmailStr, SecretStr

from app.schemas.user_schema import UserInfoSchema
from shopping_shared.schemas.base_schema import BaseSchema


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


class TokenResponseSchema(BaseSchema):
    """Schema for token responses."""
    access_token: str
    token_type: str = "Bearer"
    refresh_token: Optional[str] = None
    expires_in_minutes: int


class ResetPasswordRequestSchema(BaseSchema):
    """Schema for reset password requests."""
    new_password: SecretStr
    email: EmailStr
    otp_code: str


class ChangePasswordRequestSchema(BaseSchema):
    """Schema for change password requests."""
    current_password: SecretStr
    new_password: SecretStr