# user-service/app/schemas/otp_schema.py
from pydantic import Field, EmailStr
from shopping_shared.schemas.base_schema import BaseSchema
from app.enums.auth import OtpAction


class OTPRequestSchema(BaseSchema):
    """Schema to request a verification OTP."""
    email: EmailStr
    action: OtpAction


class RegisterVerifyRequestSchema(BaseSchema):
    """
    Schema for verifying account registration (activation).
    Implies action=REGISTER.
    """
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
