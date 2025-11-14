from fastapi import HTTPException
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from .crud_base import CRUDBase
from models.storage import StorableUnit
from schemas.storable_unit_schemas import StorableUnitCreate, StorableUnitUpdate

class StorableUnitCRUD(CRUDBase[StorableUnit, StorableUnitCreate, StorableUnitUpdate]):
    def consume(self, db: Session, id: int, consume_quantity: int) -> tuple[str, Optional[StorableUnit]]:
        unit = db.execute(
            select(StorableUnit)
            .where(StorableUnit.unit_id == id)
            .with_for_update()
        ).scalar_one_or_none()

        if unit is None:
            raise HTTPException(status_code=404, detail=f"StorableUnit with id={id} not found")
        if unit.package_quantity > consume_quantity:
            unit.package_quantity -= consume_quantity
            db.add(unit)
            try:
                db.commit()
                db.refresh(unit)
            except IntegrityError as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
            return "Consumed", unit
        elif unit.package_quantity == consume_quantity:
            db.delete(unit)
            db.commit()
            return "Consumed and deleted", None
        else:
            raise HTTPException(status_code=400, detail=f"Cannot consume from StorableUnit with id={id}: insufficient quantity (available: {unit.package_quantity}, requested: {consume_quantity})")


