# app/schemas/auth/access_token_schema.py
from shopping_shared.schemas.base_schema import BaseSchema

class AccessTokenResponse(BaseSchema):
    """Schema cho dữ liệu access token trả về trong JSON body."""
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int