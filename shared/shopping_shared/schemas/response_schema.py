# shared/shopping_shared/schemas/response_schema.py
from typing import Generic, TypeVar, Optional
from sanic_ext import openapi
from shopping_shared.schemas.base_schema import BaseSchema

T = TypeVar('T')

@openapi.component
class GenericResponse(BaseSchema, Generic[T]):
    """
    A generic response model to standardize API outputs.
    """
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None

@openapi.component
class PaginationResponse(GenericResponse[list[T]]):
    """
    A generic pagination response model to standardize API outputs for lists.
    """
    data: list[T]
    page: int
    page_size: int
    total_items: int
    total_pages: int
