from fastapi import APIRouter, Depends, Query, Body, status, HTTPException, Path
from typing import TypeVar, Type, Optional
from sqlalchemy import inspect
from sqlalchemy.orm import Session, DeclarativeBase
from pydantic import BaseModel
from core.database import get_db

from shopping_shared.crud.crud_base import CRUDBase
from shopping_shared.schemas.cursor_pagination_schema import CursorPaginationResponse
from shopping_shared.middleware.fastapi_auth import CurrentUser

"""
    Generic CRUD router factory for reuse across CRUD operations of different models
"""

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)

def create_crud_router(
        *,
        model: Type[ModelType],
        crud_base: CRUDBase,
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        response_schema: Type[ResponseSchemaType],
        prefix: str = "",
        tags: Optional[list[str]] = None
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get(
        "/{id}",
        response_model=response_schema,
        status_code=status.HTTP_200_OK,
        description=f"Retrieve a {crud_base.model.__name__} by its unique ID. Returns 404 if the {crud_base.model.__name__} does not exist."
    )
    def get_item(current_user: CurrentUser, id: int = Path(..., ge=1), db: Session = Depends(get_db)):
        # Verify user has access to the resource
        # TODO: Add resource access validation
        obj = crud_base.get(db, id)
        if obj is None:
            raise HTTPException(status_code=404, detail=f"{crud_base.model.__name__} with id={id} not found")
        return obj

    @router.get(
        "/",
        response_model=CursorPaginationResponse[response_schema],                                 # type: ignore
        status_code=status.HTTP_200_OK,
        description=(
                f"Retrieve a list of {crud_base.model.__name__} items. "
                "Supports pagination with cursor and limit."
        )
    )
    def get_many_items(
        current_user: CurrentUser,
        cursor: Optional[int] = Query(None, ge=0, description="Cursor for pagination (ID of the last item from previous page)"),
        limit: int = Query(100, ge=1, description="Maximum number of results to return"),
        db: Session = Depends(get_db)
    ):
        # Verify user has access to the resources
        # TODO: Add resource access validation
        items = crud_base.get_many(db, cursor=cursor, limit=limit)
        pk = inspect(crud_base.model).primary_key[0]
        next_cursor = getattr(items[-1], pk.name) if items and len(items) == limit else None
        return CursorPaginationResponse(
            data=list(items),
            next_cursor=next_cursor,
            size=len(items)
        )

    @router.post(
        "/",
        response_model=response_schema,
        status_code=status.HTTP_201_CREATED,
        description=f"Create a new {crud_base.model.__name__} with the provided data. Returns the created {crud_base.model.__name__}."
    )
    def create_item(current_user: CurrentUser, obj_in: create_schema = Body(...), db: Session = Depends(get_db)):
        # type: ignore
        return crud_base.create(db, obj_in)


    @router.put(
        "/{id}",
        response_model=response_schema,
        status_code=status.HTTP_200_OK,
        description=(
                f"Update an existing {crud_base.model.__name__} identified by its ID with the provided data. "
                f"Returns 404 if the {crud_base.model.__name__} does not exist."
        )
    )
    def update_item(current_user: CurrentUser, id: int = Path(..., ge=1), obj_in: update_schema = Body(...), db: Session = Depends(get_db)):         # type: ignore
        # Verify user has permission to update the resource
        # TODO: Add permission validation
        db_obj = crud_base.get(db, id)
        if db_obj is None:
            raise HTTPException(status_code=404, detail=f"{crud_base.model.__name__} with id={id} not found")
        return crud_base.update(db, obj_in, db_obj)

    @router.delete(
        "/{id}",
        status_code=status.HTTP_204_NO_CONTENT,
        description=(
                f"Delete an existing {crud_base.model.__name__} by its unique ID. "
                f"Returns 204 No Content on success. Returns 404 if the {crud_base.model.__name__} does not exist."
        )
    )
    def delete_item(current_user: CurrentUser, id: int = Path(..., ge=1), db: Session = Depends(get_db)):
        # Verify user has permission to delete the resource
        # TODO: Add permission validation
        db_obj = crud_base.get(db, id)
        if db_obj is None:
            raise HTTPException(status_code=404, detail=f"{crud_base.model.__name__} with id={id} not found")
        crud_base.delete(db, id)

    return router
