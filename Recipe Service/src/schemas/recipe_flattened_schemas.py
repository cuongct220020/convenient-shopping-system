from pydantic import BaseModel
from .ingredient_schemas import IngredientResponse

class RecipeQuantityInput(BaseModel):
    recipe_id: int
    quantity: int

class AggregatedIngredientsResponse(BaseModel):
    all_ingredients: dict[int, tuple[float, IngredientResponse]]