from pydantic import BaseModel, field_validator
from typing import List
from enums.measurement_unit import MeasurementUnit

class CountableIngredient(BaseModel):
    ingredient_id: int
    ingredient_name: str
    quantity: int

class UncountableIngredient(BaseModel):
    ingredient_id: int
    ingredient_name: str
    quantity: int
    unit: str

    @field_validator("unit")
    @classmethod
    def map_unit_to_enum(cls, v):
        v_str = str(v).upper()
        if v_str not in MeasurementUnit.__members__:
            raise ValueError(
                f"Invalid unit: {v}. Must be one of {list(MeasurementUnit.__members__.keys())}"
            )
        return v_str

class RecipeIn(BaseModel):
    recipe_name: str
    default_servings: int
    instructions: str
    countable_ingredients: List[CountableIngredient]
    uncountable_ingredients: List[UncountableIngredient]

class RecipeOut(BaseModel):
    recipe_id: int
    recipe_name: str
    default_servings: int
    instructions: str
    countable_ingredients: List[CountableIngredient]
    uncountable_ingredients: List[UncountableIngredient]