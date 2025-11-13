from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Literal, Annotated
from typing_extensions import TypeAlias
from enums.c_measurement_unit import CMeasurementUnit
from enums.uc_measurement_unit import UCMeasurementUnit

class IngredientBase(BaseModel):
    type: Literal["countable_ingredient", "uncountable_ingredient", "bulk_ingredient"]
    estimated_shelf_life: Optional[int] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carb: Optional[float] = None
    fiber: Optional[float] = None
    calories: Optional[float] = None
    estimated_price: Optional[int] = None
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
    c_measurement_unit: CMeasurementUnit

class UncountableIngredientCreate(IngredientBase):
    type: Literal["uncountable_ingredient"]
    component_name: str
    uc_measurement_unit: UCMeasurementUnit

class BulkIngredientCreate(UncountableIngredientCreate):
    type: Literal["bulk_ingredient"]

IngredientCreate: TypeAlias = Annotated[
    CountableIngredientCreate | UncountableIngredientCreate | BulkIngredientCreate,
    Field(discriminator='type')
]

# === Update ===
class CountableIngredientUpdate(IngredientBase):
    type: Literal["countable_ingredient"]
    component_name: Optional[str] = None

class UncountableIngredientUpdate(IngredientBase):
    type: Literal["uncountable_ingredient"]
    component_name: Optional[str] = None

class BulkIngredientUpdate(UncountableIngredientUpdate):
    type: Literal["bulk_ingredient"]

IngredientUpdate: TypeAlias = Annotated[
    CountableIngredientUpdate | UncountableIngredientUpdate | BulkIngredientUpdate,
    Field(discriminator='type')
]

# === Response ===
class CountableIngredientResponse(IngredientBase):
    type: Literal["countable_ingredient"]
    component_id: int
    component_name: str
    c_measurement_unit: CMeasurementUnit

class UncountableIngredientResponse(IngredientBase):
    type: Literal["uncountable_ingredient"]
    component_id: int
    component_name: str
    uc_measurement_unit: UCMeasurementUnit

class BulkIngredientResponse(UncountableIngredientResponse):
    type: Literal["bulk_ingredient"]

IngredientResponse: TypeAlias = Annotated[
    CountableIngredientResponse | UncountableIngredientResponse | BulkIngredientResponse,
    Field(discriminator='type')
]

