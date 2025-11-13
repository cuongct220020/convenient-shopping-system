from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from schemas.recipe_schema import RecipeIn, RecipeOut
from services.recipe_crud import get_all_recipes, create_recipe

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get(
    "/",
    response_model=List[RecipeOut],
    status_code=status.HTTP_200_OK,
    description="Fetches and returns a list of all recipes with their details."
)
async def get_all_recipes_api(db: Session = Depends(get_db)):
    recipes = await get_all_recipes(db)
    return recipes

@router.post(
    "/",
    response_model=RecipeOut,
    status_code=status.HTTP_201_CREATED,
    description="Creates a new recipe with the provided details."
)
async def create_recipe_api(recipe_in: RecipeIn, db: Session = Depends(get_db)):
    try:
        recipe = await create_recipe(db, recipe_in)
        return recipe
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

