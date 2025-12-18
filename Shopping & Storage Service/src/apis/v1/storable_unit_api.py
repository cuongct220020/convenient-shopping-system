from fastapi import APIRouter, status, Depends, Body
from sqlalchemy.orm import Session
from services.storable_unit_crud import StorableUnitCRUD
from schemas.storable_unit_schemas import StorableUnitCreate, StorableUnitUpdate, StorableUnitResponse, StorableUnitConsumeResponse
from models.storage import StorableUnit
from shared.shopping_shared.crud.crud_router_base import create_crud_router
from shared.shopping_shared.databases.fastapi_database import get_db

storable_unit_crud = StorableUnitCRUD(StorableUnit)

storable_unit_router = APIRouter(
    prefix="/v1/storable_units",
    tags=["storable_units"]
)

crud_router = create_crud_router(
    model=StorableUnit,
    crud_base=storable_unit_crud,
    create_schema=StorableUnitCreate,
    update_schema=StorableUnitUpdate,
    response_schema=StorableUnitResponse
)

storable_unit_router.include_router(crud_router)

@storable_unit_router.post(
    "/{id}/consume",
    response_model=StorableUnitConsumeResponse,
    status_code=status.HTTP_200_OK,
    description=(
            "Consume a specified quantity from a storable unit. If the quantity reaches zero, the unit is deleted."
            "Returns 404 if the StorableUnit does not exist."
            "Returns 400 if the requested quantity exceeds available quantity."
    )
)
def consume_storable_unit(id: int, consume_quantity: int = Body(..., gt=0), db: Session = Depends(get_db)):
    message, storable_unit = storable_unit_crud.consume(db, id, consume_quantity)
    return StorableUnitConsumeResponse(message=message, storable_unit=storable_unit)

