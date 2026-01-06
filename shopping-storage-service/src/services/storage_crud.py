from shopping_shared.crud.crud_base import CRUDBase
from models.storage import Storage
from schemas.storage_schemas import StorageCreate, StorageUpdate

class StorageCRUD(CRUDBase[Storage, StorageCreate, StorageUpdate]):
    pass