from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from sqlalchemy.inspection import inspect
from shopping_shared.crud.crud_base import CRUDBase
from models.storage import Storage
from schemas.storage_schemas import StorageCreate, StorageUpdate
from enums.storage_type import StorageType

class StorageCRUD(CRUDBase[Storage, StorageCreate, StorageUpdate]):
    def filter(
        self,
        db: Session,
        group_id: Optional[UUID] = None,
        storage_type: Optional[StorageType] = None,
        cursor: Optional[int] = None,
        limit: int = 100
    ) -> Sequence[Storage]:
        stmt = select(Storage).options(selectinload(Storage.storage_unit_list))

        if group_id is not None:
            stmt = stmt.where(Storage.group_id == group_id)

        if storage_type is not None:
            stmt = stmt.where(Storage.storage_type == storage_type)

        pk = inspect(Storage).primary_key[0]
        stmt = stmt.order_by(pk.desc())
        if cursor is not None:
            stmt = stmt.where(pk < cursor)
        stmt = stmt.limit(limit)
        return db.execute(stmt).scalars().all()