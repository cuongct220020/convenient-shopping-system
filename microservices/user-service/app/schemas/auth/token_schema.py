# app/schemas/auth/token_schema.py
from shopping_shared.schemas.base_schema import BaseSchema

class TokenData(BaseSchema):
    """Consolidated token data."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
