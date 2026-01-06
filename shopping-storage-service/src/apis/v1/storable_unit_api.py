from fastapi import APIRouter, status, Depends, Body, HTTPException, Query, BackgroundTasks, Path
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import Optional, List
from uuid import UUID
from services.storable_unit_crud import StorableUnitCRUD
from schemas.storable_unit_schemas import StorableUnitCreate, StorableUnitUpdate, StorableUnitResponse, StorableUnitStackedResponse
from models.storage import StorableUnit
from shared.shopping_shared.schemas.cursor_pagination_schema import GenericResponse, CursorPaginationResponse
from core.database import get_db

storable_unit_crud = StorableUnitCRUD(StorableUnit)

storable_unit_router = APIRouter(
    prefix="/v1/storable_units",
    tags=["storable_units"]
)

@storable_unit_router.get(
    "/filter",
    response_model=CursorPaginationResponse[StorableUnitResponse],
    status_code=status.HTTP_200_OK,
    description="Filter StorableUnits by group_id, storage_id, and/or unit_name. Supports pagination with cursor and limit."
)
def filter_units(
    group_id: Optional[UUID] = Query(None, description="Filter by group ID"),
    storage_id: Optional[int] = Query(None, ge=1, description="Filter by storage ID"),
    unit_name: Optional[List[str]] = Query(None, description="Filter by unit name(s)"),
    cursor: Optional[int] = Query(None, ge=0, description="Cursor for pagination (ID of the last item from previous page)"),
    limit: int = Query(100, ge=1, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    storable_units = storable_unit_crud.filter(
        db,
        group_id=group_id,
        storage_id=storage_id,
        unit_name=unit_name,
        cursor=cursor,
        limit=limit
    )
    pk = inspect(StorableUnit).primary_key[0]
    next_cursor = getattr(storable_units[-1], pk.name) if storable_units and len(storable_units) == limit else None
    return CursorPaginationResponse(
        data=[StorableUnitResponse.model_validate(u) for u in storable_units],
        next_cursor=next_cursor,
        size=len(storable_units)
    )

@storable_unit_router.get(
    "/stacked",
    response_model=CursorPaginationResponse[StorableUnitStackedResponse],
    status_code=status.HTTP_200_OK,
    description="Retrieve a list of stacked StorableUnits. Units are grouped by common fields (unit_name, storage_id, component_id, content_type, content_quantity, content_unit). Supports pagination with cursor and limit."
)
def get_stacked_units(
    storage_id: int = Query(..., ge=1, description="The storage ID to get stacked units from"),
    cursor: Optional[int] = Query(None, ge=0, description="Cursor for pagination (ID of the last item from previous page)"),
    limit: int = Query(100, ge=1, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    storable_units = storable_unit_crud.get_stacked(db, storage_id, cursor, limit)
    data = [StorableUnitStackedResponse(**unit) for unit in storable_units]
    next_cursor = storable_units[-1]["row_num"] if storable_units and len(storable_units) == limit else None
    return CursorPaginationResponse(
        data=data,
        next_cursor=next_cursor,
        size=len(storable_units)
    )


@storable_unit_router.get(
    "/{id}",
    response_model=StorableUnitResponse,
    status_code=status.HTTP_200_OK,
    description="Retrieve a StorableUnit by its unique ID. Returns 404 if the StorableUnit does not exist."
)
def get_unit(id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    storable_unit = storable_unit_crud.get(db, id)
    if storable_unit is None:
        raise HTTPException(status_code=404, detail=f"StorableUnit with id={id} not found")
    return storable_unit


@storable_unit_router.get(
    "/",
    response_model=CursorPaginationResponse[StorableUnitResponse],
    status_code=status.HTTP_200_OK,
    description="Retrieve a list of StorableUnits. Supports pagination with cursor and limit."
)
def get_many_units(
    cursor: Optional[int] = Query(None, ge=0, description="Cursor for pagination (ID of the last item from previous page)"),
    limit: int = Query(100, ge=1, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    storable_units = storable_unit_crud.get_many(db, cursor=cursor, limit=limit)
    pk = inspect(StorableUnit).primary_key[0]
    next_cursor = getattr(storable_units[-1], pk.name) if storable_units and len(storable_units) == limit else None
    return CursorPaginationResponse(
        data=list(storable_units),
        next_cursor=next_cursor,
        size=len(storable_units)
    )

@storable_unit_router.post(
    "/",
    response_model=StorableUnitResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new StorableUnit."
)
def create_unit(
        background_tasks: BackgroundTasks,
        obj_in: StorableUnitCreate = Body(..., description="Data to create a new StorableUnit"),
        db: Session = Depends(get_db)):
    return storable_unit_crud.create(db, obj_in, background_tasks)


@storable_unit_router.put(
    "/{id}",
    response_model=StorableUnitResponse,
    status_code=status.HTTP_200_OK,
    description="Update a StorableUnit by its unique ID. Returns 404 if the StorableUnit does not exist."
)
def update_unit(
    id: int = Path(..., ge=1),
    obj_in: StorableUnitUpdate = Body(..., description="Data to update the StorableUnit"),
    db: Session = Depends(get_db)
):
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
def consume_unit(
    background_tasks: BackgroundTasks,
    id: int = Path(..., ge=1),
    consume_quantity: int = Query(..., ge=1, description="The quantity to consume"),
    db: Session = Depends(get_db)
):
    message, storable_unit = storable_unit_crud.consume(db, id, consume_quantity, background_tasks)
    return GenericResponse(
        message=message,
        data=StorableUnitResponse.model_validate(storable_unit) if storable_unit else None
    )

