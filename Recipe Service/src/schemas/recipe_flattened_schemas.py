from pydantic import BaseModel, Field
from typing import Optional
from .ingredient_schemas import IngredientResponse

class RecipeQuantityInput(BaseModel):
    recipe_id: int
    quantity: int = Field(1, ge=1)

class AggregatedIngredientsResponse(BaseModel):
    all_ingredients: dict[int, tuple[float, IngredientResponse]]

class FlattenedIngredientItem(BaseModel):
    quantity: float
    ingredient: IngredientResponse
    available: Optional[list] = None

class FlattenedIngredientsResponse(BaseModel):
    ingredients: list[FlattenedIngredientItem]