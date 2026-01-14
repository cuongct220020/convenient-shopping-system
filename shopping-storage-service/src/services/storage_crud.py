from typing import Optional, Sequence
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from sqlalchemy.inspection import inspect
from shopping_shared.crud.crud_base import CRUDBase
from models.storage import Storage
from schemas.storage_schemas import StorageCreate, StorageUpdate

class StorageCRUD(CRUDBase[Storage, StorageCreate, StorageUpdate]):
    def get(self, db: Session, id: int) -> Optional[Storage]:
        return db.execute(
            select(Storage)
            .options(selectinload(Storage.storage_unit_list))
            .where(Storage.storage_id == id)
        ).scalars().first()

    def get_many(self, db: Session, cursor: Optional[int] = None, limit: int = 100) -> Sequence[Storage]:
        pk = inspect(Storage).primary_key[0]
        stmt = (
            select(Storage)
            .options(selectinload(Storage.storage_unit_list))
            .order_by(pk.desc())
            .limit(limit)
        )
        if cursor is not None:
            stmt = stmt.where(pk < cursor)
        return db.execute(stmt).scalars().all()