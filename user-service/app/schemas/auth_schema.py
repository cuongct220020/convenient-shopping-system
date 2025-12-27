# user-service/app/schemas/auth_schema.py
from typing import Optional
from pydantic import Field, EmailStr, SecretStr


from shopping_shared.schemas.base_schema import BaseSchema


class RegisterRequestSchema(BaseSchema):
    """Schema for user registration requests."""
    username: str = Field(
        ...,
        description="The username of the user",
        examples=["user1", "user2"],
        min_length=3,
        max_length=50
    )
    email: EmailStr = Field(
        ...,
        description="The email address of the user",
        examples=["user1@example.com", "user2@example.com"],
        min_length=3,
        max_length=50
    )
    password: SecretStr = Field(
        ...,
        description="The password of the user",
        examples=["user1", "user2"],
        min_length=3,
        max_length=255
    )
    first_name: Optional[str] = Field(
        None,
        description="The first name of the user",
        examples=["Cuong", "Bao"],
        min_length=3,
        max_length=255
    )
    last_name: Optional[str] = Field(
        None,
        description="The last name of the user",
        examples=["Dang", "Nguyen"],
        min_length=3,
        max_length=255
    )


class LoginRequestSchema(BaseSchema):
    """Schema for user login requests."""
    identifier: str = Field(
        ...,
        description="Username or Email address of the user",
        examples=["cuongct0902", "cuongct@example.com"],
        min_length=3,
        max_length=255,
    )
    password: SecretStr = Field(

    )


class TokenResponseSchema(BaseSchema):
    """Schema for token responses."""
    access_token: str
    token_type: str = "Bearer"
    expires_in_minutes: int
    is_active: bool


class ResetPasswordRequestSchema(BaseSchema):
    """Schema for reset password requests."""
    new_password: SecretStr
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class ChangePasswordRequestSchema(BaseSchema):
    """Schema for change password requests."""
    current_password: SecretStr
    new_password: SecretStr


class RequestEmailChangeSchema(BaseSchema):
    """Schema for requesting an email change (Step 1)."""
    new_email: EmailStr


class ConfirmEmailChangeRequestSchema(BaseSchema):
    """Schema for confirming an email change with OTP (Step 2)."""
    new_email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
