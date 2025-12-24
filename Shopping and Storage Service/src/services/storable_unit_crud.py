from fastapi import HTTPException
from typing import Optional, Sequence, Union, List, Dict, Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func, desc, RowMapping
from sqlalchemy.inspection import inspect
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.storage import StorableUnit, Storage
from schemas.storable_unit_schemas import StorableUnitCreate, StorableUnitUpdate, StorableUnitStackedResponse


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

    def get(self, db: Session, id: int, stacked: bool = False) -> Optional[StorableUnit | StorableUnitStackedResponse]:
        if not stacked:
            return super().get(db, id)
        ref1 = aliased(StorableUnit)
        ref2 = aliased(StorableUnit)
        unit = db.execute(
            select(
                ref1.unit_name,
                ref1.storage_id,
                ref1.component_id,
                ref1.content_type,
                ref1.content_quantity,
                ref1.content_unit,
                func.sum(ref1.package_quantity).label("package_quantity"),
                func.json_agg(
                    func.json_build_object(
                        "unit_id", ref1.unit_id,
                        "added_date", ref1.added_date,
                        "expiration_date", ref1.expiration_date,
                    ).order_by(ref1.added_date)
                ).label("batch"),
            )
            .join(
                ref2,
                (ref2.storage_id == ref1.storage_id)
                & (ref2.unit_name == ref1.unit_name)
                & (ref2.component_id.is_not_distinct_from(ref1.component_id))                       # type: ignore
                & (ref2.content_quantity.is_not_distinct_from(ref1.content_quantity))               # type: ignore
                & (ref2.content_unit.is_not_distinct_from(ref1.content_unit))                       # type: ignore
            )
            .group_by(
                ref1.unit_name,
                ref1.storage_id,                                                            # type: ignore
                ref1.component_id,                                                                  # type: ignore
                ref1.content_type,
                ref1.content_quantity,                                                              # type: ignore
                ref1.content_unit,
            )
        ).mappings().one_or_none()
        if unit is None:
            return None
        return StorableUnitStackedResponse(**unit)


    def get_many(self, db: Session, cursor: Optional[int] = None, limit: int = 100, stacked: bool = False)\
            -> Sequence[StorableUnit | RowMapping]:
        if not stacked:
            return super().get_many(db, cursor, limit)
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




