from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from enums.uc_measurement_unit import UCMeasurementUnit

class StorableUnitCreate(BaseModel):
    unit_name: str
    storage_id: int = Field(gt=0)
    package_quantity: int = Field(1, ge=1)
    component_id: Optional[int] = Field(None, gt=0)
    content_type: Optional[str] = None
    content_quantity: Optional[float] = Field(None, gt=0)
    content_unit: Optional[UCMeasurementUnit] = None
    expiration_date: Optional[datetime] = None

    model_config = ConfigDict(extra="forbid")

class StorableUnitUpdate(BaseModel):
    unit_name: Optional[str] = None
    expiration_date: Optional[datetime] = None

    model_config = ConfigDict(extra="forbid")

class StorableUnitResponse(BaseModel):
    unit_id: int
    unit_name: str
    storage_id: int
    package_quantity: Optional[int] = 1
    component_id: Optional[int] = None
    content_type: Optional[str] = None
    content_quantity: Optional[float] = None
    content_unit: Optional[UCMeasurementUnit] = None
    added_date: datetime
    expiration_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
