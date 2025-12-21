from pydantic import BaseModel, conint
from .ingredient_schemas import IngredientResponse

RecipeId = conint(ge=1)

class RecipeFlattenedResponse(BaseModel):
    recipe_id: int
    all_ingredients: dict[int, tuple[float, IngredientResponse]]