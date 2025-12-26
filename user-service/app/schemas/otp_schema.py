# user-service/app/schemas/otp_schema.py
from pydantic import Field, EmailStr
from shopping_shared.schemas.base_schema import BaseSchema
from app.enums.auth import OtpAction


class OTPRequestSchema(BaseSchema):
    """Schema to request a verification OTP."""
    email: EmailStr
    action: OtpAction


class OTPVerifyRequestSchema(BaseSchema):
    """
    Schema primarily used for verifying account activation (REGISTER).
    Other actions like Reset Password or Change Email should use their specific schemas
    to ensure atomic verification and execution.
    """
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    action: OtpAction
