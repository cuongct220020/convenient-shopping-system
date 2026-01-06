from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Literal, List
from enums.plan_status import PlanStatus


class PlanItemBase(BaseModel):
    type: Literal["countable_ingredient", "uncountable_ingredient"]
    unit: str
    quantity: float = Field(gt=0)
    component_id: int = Field(ge=0)
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
    assignee_id: Optional[int]
    shopping_list: List[PlanItemBase]
    others: dict
    plan_status: PlanStatus

    model_config = ConfigDict(from_attributes=True)

class ReportUnitBase(BaseModel):
    storage_id: int = Field(ge=1)
    package_quantity: int = Field(1, gt=0)
    unit_name: str
    component_id: Optional[int] = None
    content_type: Optional[Literal["countable_ingredient", "uncountable_ingredient"]] = None
    content_quantity: Optional[float] = None
    content_unit: Optional[str] = None
    expiration_date: Optional[datetime] = None

    @model_validator(mode='after')
    def check_component_content(cls, model):
        if bool(model.component_id) != bool(model.content_type):
            raise ValueError('component_id and content_type must either both be set or both be None')

        if model.content_type == 'countable_ingredient':
            if model.content_quantity is not None or model.content_unit is not None:
                raise ValueError('For countable_ingredient, content_quantity and content_unit must be None')
        elif model.content_type == 'uncountable_ingredient':
            if model.content_quantity is None or model.content_unit is None:
                raise ValueError('For uncountable_ingredient, content_quantity and content_unit must be set')

        return model

class PlanReport(BaseModel):
    plan_id: int = Field(ge=1)
    report_content: List[ReportUnitBase]
    spent_amount: int = Field(0, ge=0)
