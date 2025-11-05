from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from services.recipe_crud import RecipeCRUD
from models.recipe_component import Recipe
from schemas.recipe import RecipeCreate, RecipeUpdate, RecipeResponse, RecipeDetailedResponse
from .crud_router_base import create_crud_router
from core.database import get_db
from utils.custom_mapping import recipe_detailed_response_mapping

recipe_crud = RecipeCRUD(Recipe)

recipe_router: APIRouter = create_crud_router(
    model=Recipe,
    crud_base=recipe_crud,
    create_schema=RecipeCreate,
    update_schema=RecipeUpdate,
    response_schema=RecipeResponse,
    prefix="/v2/recipes",
    tags=["Recipes"]
)

@recipe_router.get(
    "/detail/{id}",
    response_model=RecipeDetailedResponse,
    status_code=status.HTTP_200_OK,
    description=f"Retrieve a Recipe with detailed information about the components by its unique ID. Returns 404 if the Recipe does not exist."
)
def get_recipe_detailed(id: int, db: Session = Depends(get_db)):
    recipe = recipe_crud.get_detail(db, id)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"Recipe with id={id} not found")
    response = recipe_detailed_response_mapping(recipe)
    return response