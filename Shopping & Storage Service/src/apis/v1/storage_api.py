from fastapi import APIRouter
from services.storage_crud import StorageCRUD
from schemas.storage_schemas import StorageCreate, StorageUpdate, StorageResponse
from models.storage import Storage
from shared.shopping_shared.crud.crud_router_base import create_crud_router

storage_crud = StorageCRUD(Storage)

storage_router = APIRouter(
    prefix="/v1/storages",
    tags=["storages"]
)

crud_router = create_crud_router(
    model=Storage,
    crud_base=storage_crud,
    create_schema=StorageCreate,
    update_schema=StorageUpdate,
    response_schema=StorageResponse
)

storage_router.include_router(crud_router)
