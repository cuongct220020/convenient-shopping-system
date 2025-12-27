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
        max_length=255
    )
    email: EmailStr = Field(
        ...,
        description="The email address of the user",
        examples=["user1@example.com", "user2@example.com"],
        min_length=3,
        max_length=255
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
        examples=["cuongct", "cuongct@example.com"],
        min_length=3,
        max_length=255,
    )
    password: SecretStr = Field(
        ...,
        description="The password of the user",
        examples=["user1", "user2"],
        min_length=3,
        max_length=255
    )


class ResetPasswordRequestSchema(BaseSchema):
    """Schema for reset password requests."""
    new_password: SecretStr = Field(
        ...,
        description="The new password of the user after type correct otp",
        examples=["new_password1", "new_password2"],
        min_length=3,
        max_length=255
    )
    email: EmailStr = Field(
        ...,
        description="The email address of the user",
        examples=["user1@example.com", "user2@example.com"],
        min_length=3,
        max_length=255
    )
    otp_code: str = Field(
        ...,
        description="6-digit OTP code",
        examples=["363636", "123123"],
        min_length=6,
        max_length=6,
    )


class ChangePasswordRequestSchema(BaseSchema):
    """Schema for change password requests."""
    current_password: SecretStr = Field(
        ...,
        description="The current password of the user",
        examples=["current_password1", "current_password2"],
        min_length=3,
        max_length=255
    )
    new_password: SecretStr = Field(
        ...,
        description="The new password of the user",
        min_length=3,
        max_length=255
    )


class RequestEmailChangeSchema(BaseSchema):
    """Schema for requesting an email change (Step 1)."""
    # email: EmailStr = Field(
    #     ...,
    #     description="The current email address of the user",
    #     examples=["cuong@example.com"],
    # )
    new_email: EmailStr = Field(
        ...,
        description="The new email address of the user",
        examples=["cuong@example.com", "cuongct@example.com"],
        min_length=3,
        max_length=255
    )


class ConfirmEmailChangeRequestSchema(BaseSchema):
    """Schema for confirming an email change with OTP (Step 2)."""
    new_email: EmailStr = Field(
        ...,
        description="The new email address of the user",
        examples=["cuong@example.com", "cuongct@example.com"],
        min_length=3,
        max_length=255
    )
    otp_code: str = Field(
        ...,
        description="6-digit OTP code",
        examples=["363636", "123123"],
        min_length=6,
        max_length=6
    )


# Response Schema
class TokenResponseSchema(BaseSchema):
    """Schema for token responses."""
    access_token: str
    token_type: str = "Bearer"
    expires_in_minutes: int
    is_active: bool