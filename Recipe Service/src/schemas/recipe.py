from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal, Annotated
from typing_extensions import TypeAlias
from .ingredient import IngredientResponse

class ComponentBase(BaseModel):
    component_id: int
    quantity: float = Field(gt=0)

class RecipeBase(BaseModel):
    image_url: Optional[str] = None
    prep_time: Optional[int] = Field(None, gt=0)
    cook_time: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None

# === Create ===
class RecipeCreate(RecipeBase):
    component_name: str
    default_servings: int = Field(1, ge=1)
    instructions: list[str]
    component_list: list[ComponentBase]

    model_config = ConfigDict(extra="forbid")

# === Update ===
class RecipeUpdate(RecipeBase):
    component_name: Optional[str] = None
    default_servings: Optional[int] = Field(None, ge=1)
    instructions: Optional[list[str]] = None
    component_list: Optional[list[ComponentBase]] = None

    model_config = ConfigDict(extra="forbid")

# === Response ===
class RecipeResponse(RecipeBase):
    component_id: int
    component_name: str
    default_servings: int
    instructions: list[str]
    component_list: list[ComponentBase]

    model_config = ConfigDict(from_attributes=True)

"""
    Nested, recursive response structure for detailed recipe information
"""

ComponentDetail: TypeAlias = Annotated[
    IngredientResponse | "RecipeDetailedResponse",
    Field(discriminator="type")
]

class ComponentDetailedBase(BaseModel):
    quantity: float
    component: ComponentDetail

class RecipeDetailedResponse(RecipeBase):
    component_id: int
    component_name: str
    type: Literal["recipe"]
    default_servings: int
    instructions: list[str]
    component_list: list[ComponentDetailedBase]

RecipeDetailedResponse.model_rebuild()
ComponentDetailedBase.model_rebuild()


class RecipeFlattenedResponse(BaseModel):
    recipe_id: int
    recipe_name: str
    all_ingredients: list[dict]

    model_config = ConfigDict(from_attributes=True)