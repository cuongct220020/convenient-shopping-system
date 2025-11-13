# app/schemas/auth/reset_password_schema.py
from pydantic import EmailStr, SecretStr, Field

from shopping_shared.schemas.base_schema import BaseSchema
from app.schemas.custom_types import PasswordStr


class ResetPasswordRequest(BaseSchema):
    """Schema for the request to reset a password using an OTP."""
    email: EmailStr
    otp_code: SecretStr = Field(..., min_length=6, max_length=6, description="The 6-digit code sent to the user's email.")
    new_password: PasswordStr
