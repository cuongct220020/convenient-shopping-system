import uuid
from fastapi import APIRouter, status, Depends, Query, HTTPException, Body, Path
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import List, Optional
from services.recipe_crud import RecipeCRUD
from services.recommender import Recommender
from models.recipe_component import Recipe
from schemas.recipe_flattened_schemas import RecipeQuantityInput, FlattenedIngredientsResponse, FlattenedIngredientItem
from schemas.recipe_schemas import RecipeCreate, RecipeUpdate, RecipeResponse, RecipeDetailedResponse
from .crud_router_base import create_crud_router
from shopping_shared.schemas.cursor_pagination_schema import CursorPaginationResponse
from core.database import get_db
from utils.custom_mapping import recipe_detailed_mapping

recipe_crud = RecipeCRUD(Recipe)

recipe_router = APIRouter(
    prefix="/v2/recipes",
    tags=["recipes"]
)

@recipe_router.get(
    "/recommend",
    response_model=List[RecipeResponse],
    status_code=status.HTTP_200_OK,
    description="Get recommended recipes for a group based on ingredient availability and tag preferences. Returns top 10 recipes."
)
def recommend_recipes(
    group_id: uuid.UUID = Query(..., description="Group ID to get recommendations for"),
    db: Session = Depends(get_db)
):
    recommender = Recommender(db)
    recipe_ids = recommender.recommend(db, group_id)
    
    if not recipe_ids:
        return []
    
    recipes = recipe_crud.get_detail(db, recipe_ids)
    recipe_map = {r.component_id: r for r in recipes}
    sorted_recipes = [recipe_map[rid] for rid in recipe_ids if rid in recipe_map]
    
    return [RecipeResponse.model_validate(r, from_attributes=True) for r in sorted_recipes]

@recipe_router.get(
    "/search",
    response_model=CursorPaginationResponse[RecipeResponse],  # type: ignore
    status_code=status.HTTP_200_OK,
    description="Search for recipes by keyword in their names or ingredients with cursor-based pagination. Returns a paginated list of matching recipes."
)
def search_recipes(
    keyword: str = Query(..., description="Keyword to search for in recipe names or ingredients"),
    cursor: Optional[int] = Query(None, ge=0, description="Cursor for pagination (ID of the last item from previous page)"),
    limit: int = Query(100, ge=1, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    items = recipe_crud.search(db, keyword=keyword, cursor=cursor, limit=limit)
    pk = inspect(Recipe).primary_key[0]
    next_cursor = getattr(items[-1], pk.name) if items and len(items) == limit else None
    return CursorPaginationResponse(
        data=list(items),
        next_cursor=next_cursor,
        size=len(items)
    )

@recipe_router.post(
    "/flattened",
    response_model=FlattenedIngredientsResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Aggregate ingredients from multiple recipes with quantity. "
        "Returns 400 if check_existence is True but group_id is not provided. "
        "Returns 404 if at least one of the Recipes does not exist."
    )
)
def get_recipe_flattened(
    recipes_with_quantity: list[RecipeQuantityInput] = Body(
        ...,
        description="List of recipes with their quantities to aggregate",
        examples=[
            [{"recipe_id": 1, "quantity": 2}, {"recipe_id": 2, "quantity": 1}],
            [{"recipe_id": 3, "quantity": 1}, {"recipe_id": 4, "quantity": 3}, {"recipe_id": 5, "quantity": 2}]
        ]
    ),
    check_existence: bool = Query(False, description="Check if ingredients exist in group inventory"),
    group_id: Optional[uuid.UUID] = Query(None, description="Group ID to check ingredient existence (required if check_existence is True)"),
    db: Session = Depends(get_db)
):
    if check_existence and group_id is None:
        raise HTTPException(
            status_code=400,
            detail="group_id is required when check_existence is True"
        )
    
    result = recipe_crud.get_flattened(recipes_with_quantity, group_id, check_existence, db)

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
            "Update an existing Recipe identified by its ID with the provided data. "
            "Returns 404 if the Recipe does not exist. "
            "Returns 400 if component list of the Recipe contains the Recipe itself to prevent infinite loop."
    )
)
def update_recipe(id: int = Path(..., ge=1, description="The unique identifier of the Recipe to update"), obj_in: RecipeUpdate = Body(..., description="Data to update the Recipe"), db: Session = Depends(get_db)):
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
def get_recipe_detailed(id: int = Path(..., ge=1, description="The unique identifier of the Recipe"), db: Session = Depends(get_db)):
    recipes = recipe_crud.get_detail(db, [id])
    if not recipes:
        raise HTTPException(status_code=404, detail=f"Recipe with id={id} not found")
    response = recipe_detailed_mapping(recipes[0])
    return response