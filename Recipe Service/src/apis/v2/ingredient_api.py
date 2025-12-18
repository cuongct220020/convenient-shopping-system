from typing import List
from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.orm import Session
from services.ingredient_crud import IngredientCRUD
from schemas.ingredient_schemas import IngredientCreate, IngredientUpdate, IngredientResponse
from models.recipe_component import Ingredient
from .crud_router_base import create_crud_router
from database import get_db

ingredient_crud = IngredientCRUD(Ingredient)

ingredient_router = APIRouter(
    prefix="/v2/ingredients",
    tags=["Ingredients"]
)

@ingredient_router.get(
    "/search",
    response_model=List[IngredientResponse],
    status_code=status.HTTP_200_OK,
    description="Search for ingredients by keyword in their names. Returns a list of matching ingredients."
)
def search_ingredients(keyword: str = Query(...), limit: int = Query(10), db: Session = Depends(get_db)):
    return ingredient_crud.search(db, keyword=keyword, limit=limit)

crud_router = create_crud_router(
    model=Ingredient,
    crud_base=ingredient_crud,
    create_schema=IngredientCreate,
    update_schema=IngredientUpdate,
    response_schema=IngredientResponse
)

ingredient_router.include_router(crud_router)