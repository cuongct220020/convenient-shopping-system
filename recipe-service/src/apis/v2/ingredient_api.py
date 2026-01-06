from typing import Optional
from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from services.ingredient_crud import IngredientCRUD
from schemas.ingredient_schemas import IngredientCreate, IngredientUpdate, IngredientResponse
from models.recipe_component import Ingredient
from enums.category import Category
from .crud_router_base import create_crud_router
from shopping_shared.schemas.cursor_pagination_schema import CursorPaginationResponse
from core.database import get_db

ingredient_crud = IngredientCRUD(Ingredient)

ingredient_router = APIRouter(
    prefix="/v2/ingredients",
    tags=["ingredients"]
)

@ingredient_router.get(
    "/search",
    response_model=CursorPaginationResponse[IngredientResponse],  # type: ignore
    status_code=status.HTTP_200_OK,
    description="Search for ingredients by keyword in their names with cursor-based pagination. Returns a paginated list of matching ingredients."
)
async def search_ingredients(
        keyword: str = Query(..., description="Keyword to search for in ingredient names"),
        cursor: Optional[int] = Query(None, ge=0, description="Cursor for pagination (ID of the last item from previous page)"),
        limit: int = Query(100, ge=1, description="Maximum number of results to return"),
        db: Session = Depends(get_db)
):
    items = ingredient_crud.search(db, keyword=keyword, cursor=cursor, limit=limit)
    pk = inspect(Ingredient).primary_key[0]
    next_cursor = getattr(items[-1], pk.name) if items and len(items) == limit else None
    return CursorPaginationResponse(
        data=list(items),
        next_cursor=next_cursor,
        size=len(items)
    )

@ingredient_router.get(
    "/filter",
    response_model=CursorPaginationResponse[IngredientResponse],
    status_code=status.HTTP_200_OK,
    description="Filter ingredients by category with cursor-based pagination. Returns a paginated list of ingredients matching the specified category."
)
def filter_ingredients_by_category(
    category: Category = Query(..., description="Category to filter ingredients by", examples=[Category.vegetables, Category.fresh_meat]),
    cursor: Optional[int] = Query(None, ge=0, description="Cursor for pagination (ID of the last item from previous page)"),
    limit: int = Query(100, ge=1, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    items = ingredient_crud.filter(db, category=category, cursor=cursor, limit=limit)
    pk = inspect(Ingredient).primary_key[0]
    next_cursor = getattr(items[-1], pk.name) if items and len(items) == limit else None
    return CursorPaginationResponse(
        data=list(items),
        next_cursor=next_cursor,
        size=len(items)
    )

crud_router = create_crud_router(
    model=Ingredient,
    crud_base=ingredient_crud,
    create_schema=IngredientCreate,
    update_schema=IngredientUpdate,
    response_schema=IngredientResponse
)

ingredient_router.include_router(crud_router)