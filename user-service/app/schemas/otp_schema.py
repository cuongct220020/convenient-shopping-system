# user-service/app/schemas/otp_schema.py
from pydantic import Field, EmailStr, SecretStr
from shopping_shared.schemas.base_schema import BaseSchema
from app.enums.auth import OtpAction



class OTPRequestSchema(BaseSchema):
    """Schema to request a verification OTP."""
    email: EmailStr
    action: OtpAction



class OTPVerifyRequestSchema(BaseSchema):
    """Schema to verify an account using an OTP."""
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    action: OtpAction