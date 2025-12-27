# shared/shopping_shared/sanic/schemas.py
from typing import Optional, TypeVar, Generic

T = TypeVar("T")

class DocGenericResponse(Generic[T]):
    """
    A generic response schema for OpenAPI documentation purposes.
    This allows sanic-ext to correctly resolve nested schemas.
    """
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None
