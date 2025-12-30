from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal, Annotated
from typing_extensions import TypeAlias
from enums.level import Level
from .ingredient_schemas import IngredientResponse

class ComponentBase(BaseModel):
    component_id: int
    quantity: float = Field(gt=0)

class RecipeBase(BaseModel):
    image_url: Optional[str] = None
    prep_time: Optional[int] = Field(None, gt=0)
    cook_time: Optional[int] = Field(None, gt=0)

# === Create ===
class RecipeCreate(RecipeBase):
    component_name: str
    level: Level
    default_servings: int = Field(1, ge=1)
    instructions: list[str]
    keywords: list[str] = Field(default_factory=list)
    component_list: list[ComponentBase]

    model_config = ConfigDict(extra="forbid")

# === Update ===
class RecipeUpdate(RecipeBase):
    component_name: Optional[str] = None
    level: Optional[Level] = None
    default_servings: Optional[int] = Field(None, ge=1)
    instructions: Optional[list[str]] = None
    keywords: Optional[list[str]] = None
    component_list: Optional[list[ComponentBase]] = None

    model_config = ConfigDict(extra="forbid")

# === Response ===
class RecipeResponse(RecipeBase):
    component_id: int
    component_name: str
    level: Level
    default_servings: int
    instructions: list[str]
    keywords: list[str]
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
    level: Level
    default_servings: int
    instructions: list[str]
    keywords: list[str]
    component_list: list[ComponentDetailedBase]

RecipeDetailedResponse.model_rebuild()
ComponentDetailedBase.model_rebuild()