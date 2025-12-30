# user-service/app/enums/auth_schema.py
from enum import Enum
from sanic_ext import openapi


@openapi.component
class OtpAction(str, Enum):
    """Enum for OTP actions."""
    REGISTER = "register"
    RESET_PASSWORD = "reset_password"
    CHANGE_EMAIL = "change_email"
