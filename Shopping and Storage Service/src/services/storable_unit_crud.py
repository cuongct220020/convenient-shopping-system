from fastapi import HTTPException
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from shared.shopping_shared.crud.crud_base import CRUDBase
from models.storage import StorableUnit, Storage
from schemas.storable_unit_schemas import StorableUnitCreate, StorableUnitUpdate
from messaging.producers.ingredient_presence_change_producer import produce_ingredient_presence_change

class StorableUnitCRUD(CRUDBase[StorableUnit, StorableUnitCreate, StorableUnitUpdate]):
    async def create(self, db: Session, obj_in: StorableUnitCreate) -> StorableUnit:
        try:
            with db.begin():
                obj_in_data = obj_in.model_dump()
                db_obj = StorableUnit(**obj_in_data)
                db.add(db_obj)
                db.refresh(db_obj)

                if db_obj.component_id is not None:
                    group_id = db_obj.storage.group_id
                    same_component_units = db.execute(
                        select(StorableUnit)
                        .join(Storage, StorableUnit.storage_id == Storage.storage_id)
                        .where(
                            Storage.group_id == group_id,
                            StorableUnit.unit_name == db_obj.unit_name
                        )
                    ).scalars().all()
                    if len(same_component_units) == 1:
                        await produce_ingredient_presence_change(group_id=group_id, component_name=db_obj.unit_name, is_present=True)
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
        return db_obj

    async def consume(self, db: Session, id: int, consume_quantity: int) -> tuple[str, Optional[StorableUnit]]:
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
                    if unit.component_id is not None:
                        group_id = unit.storage.group_id
                        same_component_units = db.execute(
                            select(StorableUnit)
                            .join(Storage, StorableUnit.storage_id == Storage.storage_id)
                            .where(
                                Storage.group_id == group_id,
                                StorableUnit.unit_name == unit.unit_name
                            )
                        ).scalars().all()
                        if len(same_component_units) == 1:
                            await produce_ingredient_presence_change(group_id=group_id, component_name=unit.unit_name, is_present=False)
                    db.delete(unit)
                    return "Consumed and deleted", None
                else:
                    unit.package_quantity -= consume_quantity
                    return "Consumed", unit
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")



