from fastapi import HTTPException
from typing import Optional, Sequence, List
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func, RowMapping
from sqlalchemy.inspection import inspect
from shopping_shared.crud.crud_base import CRUDBase
from models.storage import StorableUnit, Storage
from schemas.storable_unit_schemas import StorableUnitCreate, StorableUnitUpdate, StorableUnitResponse
from core.messaging import kafka_manager
from shopping_shared.messaging.topics import COMPONENT_EXISTENCE_TOPIC


class StorableUnitCRUD(CRUDBase[StorableUnit, StorableUnitCreate, StorableUnitUpdate]):
    async def create(self, db: Session, obj_in: StorableUnitCreate) -> StorableUnit:
        db_obj = super().create(db, obj_in)
        storage = db.get(Storage, db_obj.storage_id)
        if storage:
            stmt = (
                select(StorableUnit.unit_name)
                .join(Storage, StorableUnit.storage_id == Storage.storage_id)
                .where(Storage.group_id == storage.group_id)
                .where(StorableUnit.component_id.isnot(None))
                .distinct()
            )
            unit_names = db.execute(stmt).scalars().all()
            payload = {
                "event_type": "update_component_existence",
                "data": {
                    "group_id": storage.group_id,  # type: ignore
                    "unit_names": unit_names,
                },
            }
            await kafka_manager.send_message(
                topic=COMPONENT_EXISTENCE_TOPIC,
                value=payload,
                key=str(storage.group_id),  # type: ignore
                wait=True,
            )
        return db_obj

    async def consume(self, db: Session, id: int,consume_quantity: int) -> tuple[str, Optional[StorableUnitResponse]]:
        try:
            with db.begin():
                unit = db.execute(
                    select(StorableUnit)
                    .where(StorableUnit.unit_id == id)
                    .with_for_update()
                ).scalar_one_or_none()

                if unit is None:
                    raise HTTPException(status_code=404, detail=f"StorableUnit with id={id} not found")

                if consume_quantity > unit.package_quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Cannot consume from StorableUnit with id={id}: "
                               f"insufficient quantity (available: {unit.package_quantity}, requested: {consume_quantity})"
                    )
                elif consume_quantity == unit.package_quantity:
                    storage = db.get(Storage, unit.storage_id)
                    db.delete(unit)
                    if storage:
                        stmt = (
                            select(StorableUnit.unit_name)
                            .join(Storage, StorableUnit.storage_id == Storage.storage_id)
                            .where(Storage.group_id == storage.group_id)
                            .where(StorableUnit.component_id.isnot(None))
                            .distinct()
                        )
                        unit_names = db.execute(stmt).scalars().all()
                        payload = {
                            "event_type": "update_component_existence",
                            "data": {
                                "group_id": storage.group_id,  # type: ignore
                                "unit_names": unit_names,
                            },
                        }
                        await kafka_manager.send_message(
                            topic=COMPONENT_EXISTENCE_TOPIC,
                            value=payload,
                            key=str(storage.group_id),  # type: ignore
                            wait=True,
                        )
                    return "Consumed and deleted", None
                else:
                    unit.package_quantity -= consume_quantity
                    return "Consumed", StorableUnitResponse.model_validate(unit)
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")

    def get_stacked(self, db: Session, storage_id: int, cursor: Optional[int] = None, limit: int = 100)\
            -> Sequence[RowMapping]:
        ref = aliased(StorableUnit)
        subq = (
            select(
                ref.unit_name,
                ref.storage_id,
                ref.component_id,
                ref.content_type,
                ref.content_quantity,
                ref.content_unit,
                func.sum(ref.package_quantity).label("package_quantity"),
                func.json_agg(
                    func.json_build_object(
                        "unit_id", ref.unit_id,
                        "added_date", ref.added_date,
                        "expiration_date", ref.expiration_date,
                    )
                ).label("batch"),
                func.min(ref.unit_id).label("row_num")
            )
            .where(ref.storage_id == storage_id)                                                # type: ignore
            .group_by(
                ref.unit_name,
                ref.storage_id,                                                                 # type: ignore
                ref.component_id,                                                               # type: ignore
                ref.content_type,
                ref.content_quantity,                                                           # type: ignore
                ref.content_unit,
            )
        ).subquery()
        stmt = select(subq)
        if cursor is not None:
            stmt = stmt.where(subq.c.row_num > cursor)
        stmt = stmt.order_by(subq.c.row_num).limit(limit)
        return db.execute(stmt).mappings().all()

    def filter(
        self,
        db: Session,
        group_id: Optional[UUID] = None,
        storage_id: Optional[int] = None,
        unit_name: Optional[List[str]] = None,
        cursor: Optional[int] = None,
        limit: int = 100
    ) -> Sequence[StorableUnit]:
        stmt = select(StorableUnit)

        if group_id is not None:
            stmt = stmt.join(Storage, StorableUnit.storage_id == Storage.storage_id)
            stmt = stmt.where(Storage.group_id == group_id)

        if storage_id is not None:
            stmt = stmt.where(StorableUnit.storage_id == storage_id)

        if unit_name is not None:
            if isinstance(unit_name, list) and len(unit_name) > 0:
                stmt = stmt.where(StorableUnit.unit_name.in_(unit_name))
            elif isinstance(unit_name, str):
                stmt = stmt.where(StorableUnit.unit_name == unit_name)

        pk = inspect(StorableUnit).primary_key[0]
        stmt = stmt.order_by(pk.desc())
        if cursor is not None:
            stmt = stmt.where(pk < cursor)
        stmt = stmt.limit(limit)
        return db.execute(stmt).scalars().all()