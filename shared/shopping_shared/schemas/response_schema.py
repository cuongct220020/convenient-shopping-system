# shopping_shared/schemas/response_schema.py
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class GenericResponse(BaseModel, Generic[T]):
    """
    A generic response model to standardize API outputs.
    """
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None

class PaginationResponse(GenericResponse[list[T]]):
    """
    A generic pagination response model to standardize API outputs for lists.
    """
    data: list[T]
    page: int
    page_size: int
    total_items: int
    total_pages: int
