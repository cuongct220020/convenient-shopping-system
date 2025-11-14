# /microservices/user-service/app/schemas/auth.py
from pydantic import Field, EmailStr, SecretStr
from shared.shopping_shared.schemas import BaseSchema

# --- Authentication Schemas ---
class RegisterRequestSchema(BaseSchema):
    """Schema for user registration requests."""
    user_name: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: SecretStr
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)

class LoginRequestSchema(BaseSchema):
    """Schema for user login requests."""
    email: EmailStr
    password: SecretStr

class TokenResponseSchema(BaseSchema):
    """Schema for token responses."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class ChangePasswordRequestSchema(BaseSchema):
    """Schema for an authenticated user to change their password."""
    current_password: SecretStr
    new_password: SecretStr
