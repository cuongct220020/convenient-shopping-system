from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Literal, List
from enums.plan_status import PlanStatus


class PlanItemBase(BaseModel):
    type: Literal["countable_ingredient", "uncountable_ingredient"]
    unit: str
    quantity: float
    component_id: int
    component_name: str

class PlanCreate(BaseModel):
    group_id: int = Field(gt=0)
    deadline: datetime
    assigner_id: int = Field(gt=0)
    shopping_list: List[PlanItemBase]
    others: Optional[dict] = None

    model_config = ConfigDict(extra="forbid")

class PlanUpdate(BaseModel):
    deadline: Optional[datetime] = None
    shopping_list: Optional[List[PlanItemBase]] = None
    others: Optional[dict] = None

    model_config = ConfigDict(extra="forbid")

class PlanResponse(BaseModel):
    plan_id: int
    group_id: int
    deadline: datetime
    last_modified: datetime
    assigner_id: int
    shopping_list: List[PlanItemBase]
    others: dict
    plan_status: PlanStatus

    model_config = ConfigDict(from_attributes=True)