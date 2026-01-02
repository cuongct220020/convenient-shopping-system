from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from enums.meal_action import MealAction
from enums.meal_type import MealType
from enums.meal_status import MealStatus

class RecipeBase(BaseModel):
    recipe_id: int = Field(gt=0)
    recipe_name: str
    servings: int = Field(gt=0)

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class MealCommand(BaseModel):
    action: MealAction
    recipe_list: Optional[List[RecipeBase]] = None

    model_config = ConfigDict(extra="forbid")

class DailyMealsCommand(BaseModel):
    date: date
    group_id: int = Field(gt=0)
    breakfast: MealCommand
    lunch: MealCommand
    dinner: MealCommand

    model_config = ConfigDict(extra="forbid")

class MealResponse(BaseModel):
    meal_id: int
    date: date
    group_id: int
    meal_type: MealType
    meal_status: MealStatus
    recipe_list: List[RecipeBase] = []

    model_config = ConfigDict(from_attributes=True)

class MealMissingResponse(BaseModel):
    date: date
    group_id: int
    meal_type: MealType
    detail: str