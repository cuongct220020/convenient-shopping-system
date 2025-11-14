# app/constants/auth.py
from enum import Enum


class OtpAction(str, Enum):
    """Enum for OTP actions."""
    REGISTER = "register"
    RESET_PASSWORD = "reset_password"
    CHANGE_EMAIL = "change_email"
