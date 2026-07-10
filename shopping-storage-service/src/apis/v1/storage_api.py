from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from services.storage_crud import StorageCRUD
from schemas.storage_schemas import StorageCreate, StorageUpdate, StorageResponse
from models.storage import Storage
from enums.storage_type import StorageType
from shopping_shared.schemas.cursor_pagination_schema import CursorPaginationResponse
from core.database import get_db
from .crud_router_base import create_crud_router

storage_crud = StorageCRUD(Storage)

storage_router = APIRouter(
    prefix="/v1/storages",
    tags=["storages"]
)

@storage_router.get(
    "/filter",
    response_model=CursorPaginationResponse[StorageResponse],
    status_code=status.HTTP_200_OK,
    description="Filter storages by group_id and/or storage_type. Supports pagination with cursor and limit."
)
def filter_storages(
    group_id: Optional[UUID] = Query(None, description="Filter by group ID"),
    storage_type: Optional[StorageType] = Query(None, description="Filter by storage type"),
    cursor: Optional[int] = Query(None, ge=0, description="Cursor for pagination (ID of the last item from previous page)"),
    limit: int = Query(100, ge=1, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    storages = storage_crud.filter(
        db,
        group_id=group_id,
        storage_type=storage_type,
        cursor=cursor,
        limit=limit
    )
    pk = inspect(Storage).primary_key[0]
    next_cursor = getattr(storages[-1], pk.name) if storages and len(storages) == limit else None
    return CursorPaginationResponse(
        data=[StorageResponse.model_validate(s) for s in storages],
        next_cursor=next_cursor,
        size=len(storages)
    )

crud_router = create_crud_router(
    model=Storage,
    crud_base=storage_crud,
    create_schema=StorageCreate,
    update_schema=StorageUpdate,
    response_schema=StorageResponse
)

storage_router.include_router(crud_router)
