from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from enums.storage_type import StorageType
from schemas.storable_unit_schemas import StorableUnitResponse

class StorageCreate(BaseModel):
    storage_name: Optional[str] = None
    storage_type: StorageType
    group_id: int

    model_config = ConfigDict(extra="forbid")

class StorageUpdate(BaseModel):
    storage_name: Optional[str] = None
    storage_type: Optional[StorageType] = None

    model_config = ConfigDict(extra="forbid")

class StorageResponse(BaseModel):
    storage_id: int
    storage_name: str
    storage_type: StorageType
    group_id: int
    storable_units: list[StorableUnitResponse]

    model_config = ConfigDict(from_attributes=True)