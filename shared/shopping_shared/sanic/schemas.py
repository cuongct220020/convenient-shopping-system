# shared/shopping_shared/sanic/schemas.py
from typing import Optional, Any
from pydantic import BaseModel

class DocGenericResponse(BaseModel):
    """
    A non-generic response schema for OpenAPI documentation purposes.
    Used with sanic-ext's @doc decorators to avoid issues with generic models.
    """
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Any] = None
