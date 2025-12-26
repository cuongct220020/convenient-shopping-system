from fastapi import APIRouter, status, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from services.recipe_crud import RecipeCRUD
from models.recipe_component import Recipe
from schemas.recipe_flattened_schemas import (
    AggregatedIngredientsResponse, 
    RecipeQuantityInput,
    FlattenedIngredientsResponse,
    FlattenedIngredientItem
)
from schemas.recipe_schemas import (
    RecipeCreate, RecipeUpdate, RecipeResponse, RecipeDetailedResponse
)
from .crud_router_base import create_crud_router
from core.database import get_db
from utils.custom_mapping import recipe_detailed_mapping, recipes_flattened_aggregated_mapping

recipe_crud = RecipeCRUD(Recipe)

recipe_router = APIRouter(
    prefix="/v2/recipes",
    tags=["Recipes"]
)

@recipe_router.get(
    "/search",
    response_model=List[RecipeResponse],
    status_code=status.HTTP_200_OK,
    description="Search for recipes by keyword in their names or ingredients. Returns a list of matching recipes."
)
async def search_recipes(keyword: str = Query(...), limit: int = Query(10), db: Session = Depends(get_db)):
    return await recipe_crud.search(db, keyword=keyword, limit=limit)

@recipe_router.post(
    "/flattened",
    response_model=FlattenedIngredientsResponse,
    status_code=status.HTTP_200_OK,
    description=f"Aggregate ingredients from multiple recipes with quantity. Returns 404 if at least one of the Recipes does not exist."
)
async def get_recipe_flattened(
    recipes_with_quantity: list[RecipeQuantityInput],
    check_existence: bool = Query(False),
    group_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    if check_existence and group_id is None:
        raise HTTPException(
            status_code=400,
            detail="group_id is required when check_existence is True"
        )
    
    result = await recipe_crud.get_flattened(recipes_with_quantity, group_id, check_existence, db)

    ingredients = [
        FlattenedIngredientItem(
            quantity=quantity,
            ingredient=ingredient_response,
            available=available
        )
        for quantity, ingredient_response, available in result
    ]
    
    return FlattenedIngredientsResponse(ingredients=ingredients)
@recipe_router.put(
    "/{id}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
    description=(
            f"Update an existing Recipe identified by its ID with the provided data. "
            "Returns 404 if the Recipe does not exist."
            "Returns 400 if component list of the Recipe contains the Recipe itself to prevent infinite loop."
    )
)
def update_recipe(id: int, obj_in: RecipeUpdate, db: Session = Depends(get_db)):
    db_obj = recipe_crud.get(db, id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail=f"Recipe with id={id} not found")
    if obj_in.component_list:
        for c in obj_in.component_list:
            if c.component_id == id:
                raise HTTPException(status_code=400, detail="component_list cannot contain self")
    return recipe_crud.update(db, obj_in, db_obj)

crud_router: APIRouter = create_crud_router(
    model=Recipe,
    crud_base=recipe_crud,
    create_schema=RecipeCreate,
    update_schema=RecipeUpdate,
    response_schema=RecipeResponse,
)

recipe_router.include_router(crud_router)

@recipe_router.get(
    "/detailed/{id}",
    response_model=RecipeDetailedResponse,
    status_code=status.HTTP_200_OK,
    description=f"Retrieve a Recipe with detailed information about the components by its unique ID. Returns 404 if the Recipe does not exist."
)
def get_recipe_detailed(id: int, db: Session = Depends(get_db)):
    recipes = recipe_crud.get_detail(db, [id])
    if not recipes:
        raise HTTPException(status_code=404, detail=f"Recipe with id={id} not found")
    response = recipe_detailed_mapping(recipes[0])
    return response