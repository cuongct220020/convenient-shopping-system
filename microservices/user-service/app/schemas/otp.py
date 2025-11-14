# /microservices/user-service/app/schemas/otp.py
from pydantic import Field, EmailStr, SecretStr
from shared.shopping_shared.schemas import BaseSchema
from app.constants.auth import OtpAction


# --- OTP Schemas ---
class SendVerificationOTPRequestSchema(BaseSchema):
    """Schema to request a verification OTP."""
    email: EmailStr
    action: OtpAction


class VerifyAccountRequestSchema(BaseSchema):
    """Schema to verify an account using an OTP."""
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    action: OtpAction


class RequestEmailChangeRequestSchema(BaseSchema):
    """Schema to request an email change."""
    new_email: EmailStr


class ConfirmEmailChangeRequestSchema(BaseSchema):
    """Schema to confirm an email change with an OTP."""
    new_email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class ResetPasswordRequestSchema(BaseSchema):
    """Schema to reset password with an OTP."""
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: SecretStr
