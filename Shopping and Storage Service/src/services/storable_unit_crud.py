from fastapi import HTTPException
from typing import Optional, Sequence, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func, desc, RowMapping
from sqlalchemy.inspection import inspect
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.storage import StorableUnit, Storage
from schemas.storable_unit_schemas import StorableUnitCreate, StorableUnitUpdate


class StorableUnitCRUD(CRUDBase[StorableUnit, StorableUnitCreate, StorableUnitUpdate]):
    def consume(self, db: Session, id: int, consume_quantity: int) -> tuple[str, Optional[StorableUnit]]:
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
                    db.delete(unit)
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