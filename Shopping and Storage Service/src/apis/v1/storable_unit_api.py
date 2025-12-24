from fastapi import APIRouter, status, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import Optional
from services.storable_unit_crud import StorableUnitCRUD
from schemas.storable_unit_schemas import StorableUnitCreate, StorableUnitUpdate, StorableUnitResponse, StorableUnitStackedResponse
from models.storage import StorableUnit
from shared.shopping_shared.schemas.response_schema import GenericResponse, PaginationResponse
from database import get_db

storable_unit_crud = StorableUnitCRUD(StorableUnit)

storable_unit_router = APIRouter(
    prefix="/v1/storable_units",
    tags=["storable_units"]
)


@storable_unit_router.get(
    "/{id}",
    response_model=StorableUnitResponse | StorableUnitStackedResponse,
    status_code=status.HTTP_200_OK,
    description="Retrieve a StorableUnit by its unique ID. Returns 404 if the StorableUnit does not exist."
)
def get_unit(id: int, stacked: bool = Query(False), db: Session = Depends(get_db)):
    storable_unit = storable_unit_crud.get(db, id, stacked)
    if storable_unit is None:
        raise HTTPException(status_code=404, detail=f"StorableUnit with id={id} not found")
    return storable_unit


@storable_unit_router.get(
    "/",
    response_model=PaginationResponse[StorableUnitResponse] | PaginationResponse[StorableUnitStackedResponse],
    status_code=status.HTTP_200_OK,
    description="Retrieve a list of StorableUnits. Supports pagination with cursor and limit."
)
def get_many_units(
    cursor: Optional[int] = Query(None, ge=0),
    limit: int = Query(100, ge=1),
    stacked: bool = Query(False),
    db: Session = Depends(get_db)
):
    storable_units = storable_unit_crud.get_many(db, cursor, limit, stacked)
    if not stacked:
        pk = inspect(StorableUnit).primary_key[0]
        next_cursor = getattr(storable_units[-1], pk.name) if storable_units and len(storable_units) == limit else None
        data=list(storable_units)
    else:
        data = [StorableUnitStackedResponse(**unit) for unit in storable_units]
        next_cursor = storable_units[-1].row_num if data and len(data) == limit else None
    return PaginationResponse(
        data=data,
        next_cursor=next_cursor,
        size=len(storable_units),
        has_more=len(storable_units) == limit
    )


@storable_unit_router.post(
    "/",
    response_model=StorableUnitResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new StorableUnit."
)
async def create_unit(obj_in: StorableUnitCreate, db: Session = Depends(get_db)):
    return storable_unit_crud.create(db, obj_in)


@storable_unit_router.put(
    "/{id}",
    response_model=StorableUnitResponse,
    status_code=status.HTTP_200_OK,
    description="Update a StorableUnit by its unique ID. Returns 404 if the StorableUnit does not exist."
)
def update_unit(id: int, obj_in: StorableUnitUpdate, db: Session = Depends(get_db)):
    storable_unit = storable_unit_crud.get(db, id)
    if storable_unit is None:
        raise HTTPException(status_code=404, detail=f"StorableUnit with id={id} not found")
    return storable_unit_crud.update(db, obj_in, storable_unit)


@storable_unit_router.post(
    "/{id}/consume",
    response_model=GenericResponse[StorableUnitResponse],
    status_code=status.HTTP_200_OK,
    description=(
        "Consume a specified quantity from a storable unit. If the quantity reaches zero, the unit is deleted. "
        "Returns 404 if the StorableUnit does not exist. "
        "Returns 400 if the requested quantity exceeds available quantity."
    )
)
async def consume_unit(id: int, consume_quantity: int = Body(..., gt=0), db: Session = Depends(get_db)):
    message, storable_unit = storable_unit_crud.consume(db, id, consume_quantity)
    return GenericResponse(
        message=message,
        data=StorableUnitResponse.model_validate(storable_unit) if storable_unit else None
    )

