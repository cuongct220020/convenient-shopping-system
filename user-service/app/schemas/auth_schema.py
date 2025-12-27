# user-service/app/schemas/auth_schema.py
from typing import Optional
from pydantic import Field, EmailStr, SecretStr, ConfigDict

from shopping_shared.schemas.base_schema import BaseSchema
from shopping_shared.schemas.response_schema import GenericResponse
from app.schemas.user_schema import UserCoreInfoSchema

# --- Request Schemas ---

class RegisterRequestSchema(BaseSchema):
    """Schema for user registration requests."""
    username: str = Field(
        ...,
        description="The username of the user",
        examples=["user1", "user2"],
        min_length=3,
        max_length=50  # 255 hơi dài cho username, 50 thường là đủ
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
        examples=["StrongPass1!", "AnotherPass2@"],
        min_length=8, # Password nên dài tối thiểu 8 ký tự
        max_length=255
    )
    first_name: Optional[str] = Field(
        default=None,
        description="The first name of the user",
        examples=["Cuong", "Bao"],
        min_length=1, # Tên có thể ngắn (ví dụ: An)
        max_length=100
    )
    last_name: Optional[str] = Field(
        default=None,
        description="The last name of the user",
        examples=["Dang", "Nguyen"],
        min_length=1,
        max_length=100
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
        examples=["password123"],
        min_length=3,
        max_length=255
    )


class ResetPasswordRequestSchema(BaseSchema):
    """Schema for reset password requests."""
    new_password: SecretStr = Field(
        ...,
        description="The new password of the user after typing correct otp",
        examples=["new_password1", "new_password2"],
        min_length=8,
        max_length=255
    )
    email: EmailStr = Field(
        ...,
        description="The email address of the user",
        examples=["user1@example.com"],
        min_length=3,
        max_length=255
    )
    otp_code: str = Field(
        ...,
        description="6-digit OTP code",
        examples=["363636", "123123"],
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$" # Đảm bảo chỉ chứa số
    )


class ChangePasswordRequestSchema(BaseSchema):
    """Schema for change password requests."""
    current_password: SecretStr = Field(
        ...,
        description="The current password of the user",
        examples=["current_password1"],
        min_length=3,
        max_length=255
    )
    new_password: SecretStr = Field(
        ...,
        description="The new password of the user",
        examples=["new_password123"],
        min_length=8,
        max_length=255
    )


class RequestEmailChangeSchema(BaseSchema):
    """Schema for requesting an email change (Step 1)."""
    new_email: EmailStr = Field(
        ...,
        description="The new email address of the user",
        examples=["new_email@example.com"],
        min_length=3,
        max_length=255
    )


class ConfirmEmailChangeRequestSchema(BaseSchema):
    """Schema for confirming an email change with OTP (Step 2)."""
    new_email: EmailStr = Field(
        ...,
        description="The new email address of the user",
        examples=["new_email@example.com"],
        min_length=3,
        max_length=255
    )
    otp_code: str = Field(
        ...,
        description="6-digit OTP code",
        examples=["123456"],
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )

# --- Response Schemas ---

class AccessTokenResponseSchema(BaseSchema):
    """Schema for token responses."""
    access_token: str = Field(
        ..., 
        description="The JWT Access Token"
    )
    token_type: str = Field(
        "Bearer", 
        description="Type of the token, usually Bearer"
    )
    expires_in_minutes: int = Field(
        ..., 
        description="Token expiration time in minutes"
    )
    is_active: bool = Field(
        ..., 
        description="Whether the user account is currently active"
    )


class LoginResponse(GenericResponse[AccessTokenResponseSchema]):
    """Response schema for successful login."""
    model_config = ConfigDict(
        json_schema_serialization_defaults={'ref_template': '#/components/schemas/{model}'}
    )


class RegisterResponse(GenericResponse[UserCoreInfoSchema]):
    """Response schema for successful registration."""
    model_config = ConfigDict(
        json_schema_serialization_defaults={'ref_template': '#/components/schemas/{model}'}
    )
