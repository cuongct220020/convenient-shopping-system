# user-service/app/schemas/otp_schema.py
from pydantic import Field, EmailStr
from shopping_shared.schemas.base_schema import BaseSchema
from app.enums.auth import OtpAction


class OTPRequestSchema(BaseSchema):
    """Schema to request a verification OTP."""
    email: EmailStr = Field(
        ...,
        description="Email address to verify OTP for.",
        examples=["user@example.com"],
        min_length=3,
        max_length=255
    )
    action: OtpAction = Field(
        ...,
        description="OTP action to perform.",
    )


class OTPVerifyRequestSchema(BaseSchema):
    """
    Schema for verifying account registration (activation).
    Implies action=REGISTER.
    """
    email: EmailStr = Field(
        ...,
        description="Email address to verify OTP for.",
        examples=["user@example.com"],
        min_length=3,
        max_length=255
    )
    otp_code: str = Field(
        ...,
        description="OTP code to verify OTP for.",
        examples=["OTP code"],
        min_length=6,
        max_length=6
    )
