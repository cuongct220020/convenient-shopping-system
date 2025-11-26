from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal, Annotated
from typing_extensions import TypeAlias
from enums.c_measurement_unit import CMeasurementUnit
from enums.uc_measurement_unit import UCMeasurementUnit
from enums.category import Category

class IngredientBase(BaseModel):
    type: Literal["countable_ingredient", "uncountable_ingredient"]
    estimated_shelf_life: Optional[int] = Field(None, ge=0)
    protein: Optional[float] = Field(None, ge=0)
    fat: Optional[float] = Field(None, ge=0)
    carb: Optional[float] = Field(None, ge=0)
    fiber: Optional[float] = Field(None, ge=0)
    calories: Optional[float] = Field(None, ge=0)
    estimated_price: Optional[int] = Field(None, ge=0)
    ingredient_tag_list: Optional[list[int]] = None

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        extra="forbid"
    )

# === Create ===
class CountableIngredientCreate(IngredientBase):
    type: Literal["countable_ingredient"]
    component_name: str
    category: Category
    c_measurement_unit: CMeasurementUnit

class UncountableIngredientCreate(IngredientBase):
    type: Literal["uncountable_ingredient"]
    component_name: str
    category: Category
    uc_measurement_unit: UCMeasurementUnit

IngredientCreate: TypeAlias = Annotated[
    CountableIngredientCreate | UncountableIngredientCreate,
    Field(discriminator='type')
]

# === Update ===
class CountableIngredientUpdate(IngredientBase):
    type: Literal["countable_ingredient"]
    component_name: Optional[str] = None
    category: Optional[Category] = None

class UncountableIngredientUpdate(IngredientBase):
    type: Literal["uncountable_ingredient"]
    component_name: Optional[str] = None
    category: Optional[Category] = None

IngredientUpdate: TypeAlias = Annotated[
    CountableIngredientUpdate | UncountableIngredientUpdate,
    Field(discriminator='type')
]

# === Response ===
class CountableIngredientResponse(IngredientBase):
    type: Literal["countable_ingredient"]
    component_id: int
    component_name: str
    category: Category
    c_measurement_unit: CMeasurementUnit

class UncountableIngredientResponse(IngredientBase):
    type: Literal["uncountable_ingredient"]
    component_id: int
    component_name: str
    category: Category
    uc_measurement_unit: UCMeasurementUnit

IngredientResponse: TypeAlias = Annotated[
    CountableIngredientResponse | UncountableIngredientResponse,
    Field(discriminator='type')
]

