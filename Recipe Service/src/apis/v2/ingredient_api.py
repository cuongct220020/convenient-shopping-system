from fastapi import APIRouter
from services.ingredient_crud import IngredientCRUD
from schemas.ingredient import IngredientCreate, IngredientUpdate, IngredientResponse
from models.recipe_component import Ingredient
from .crud_router_base import create_crud_router

ingredient_crud = IngredientCRUD(Ingredient)

ingredient_router: APIRouter = create_crud_router(
    model=Ingredient,
    crud_base=ingredient_crud,
    create_schema=IngredientCreate,
    update_schema=IngredientUpdate,
    response_schema=IngredientResponse,
    prefix="/v2/ingredients",
    tags=["Ingredients"]
)