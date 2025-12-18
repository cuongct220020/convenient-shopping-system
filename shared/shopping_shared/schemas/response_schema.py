# shared/shopping_shared/schemas/response_schema.py
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar('T')

class GenericResponse(BaseModel, Generic[T]):
    """
    A generic response model to standardize API outputs.
    """
    message: Optional[str] = None
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True

class PaginationResponse(GenericResponse[list[T]], Generic[T]):
    """
    A generic pagination response model to standardize API outputs for lists.
    """
    data: List[T]
    next_cursor: Optional[int] = None
    size: int
    has_more: bool
