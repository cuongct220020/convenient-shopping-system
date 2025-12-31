from fastapi import HTTPException, BackgroundTasks
from typing import Optional, Sequence, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func, desc, RowMapping
from sqlalchemy.inspection import inspect
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.storage import StorableUnit, Storage
from schemas.storable_unit_schemas import StorableUnitCreate, StorableUnitUpdate
from messaging.producers.component_existence_producer import publish_component_existence_update


class StorableUnitCRUD(CRUDBase[StorableUnit, StorableUnitCreate, StorableUnitUpdate]):
    def create(
        self,
        db: Session,
        obj_in: StorableUnitCreate,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> StorableUnit:
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
            background_tasks.add_task(
                publish_component_existence_update,
                storage.group_id,                                                               # type: ignore
                unit_names
            )

        return db_obj

    def consume(
        self,
        db: Session,
        id: int,
        consume_quantity: int,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> tuple[str, Optional[StorableUnit]]:
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
                        background_tasks.add_task(
                            publish_component_existence_update,
                            storage.group_id,                                   # type: ignore
                            unit_names
                        )
                    return "Consumed and deleted", None
                else:
                    unit.package_quantity -= consume_quantity
                    return "Consumed", unit
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
                    ).order_by(ref.added_date)
                ).label("batch"),
                func.row_number().over(order_by=desc(ref.added_date)).label("row_num")          # type: ignore
            )
            .where(ref.storage_id == storage_id)                                                # type: ignore
            .group_by(
                ref.unit_name,
                ref1.storage_id,  # type: ignore
                ref.component_id,  # type: ignore
                ref.content_type,
                ref.content_quantity,  # type: ignore
                ref.content_unit,
            )
        ).subquery()
        stmt = select(subq)
        if cursor is not None:
            stmt = stmt.where(subq.c.row_num > cursor)
        stmt = stmt.limit(limit)
        return db.execute(stmt).mappings().all()

    def filter(
        self,
        db: Session,
        group_id: Optional[int] = None,
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