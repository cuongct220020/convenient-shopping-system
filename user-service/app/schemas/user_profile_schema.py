# user-service/app/schemas/user_bp.py
from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import Field

from shopping_shared.schemas.base_schema import BaseSchema
from app.enums import UserGender, ActivityLevel, HealthCondition, HealthGoal

class AddressSchema(BaseSchema):
    ward: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    province: Optional[str] = Field(None, max_length=100)


# User Identity Profile Schemas
class UserIdentityProfileCreateSchema(BaseSchema):
    user_id: UUID
    gender: Optional[UserGender] = None
    date_of_birth: Optional[date] = None
    occupation: Optional[str] = Field(None, max_length=255)
    address: Optional[AddressSchema] = None


class UserIdentityProfileUpdateSchema(BaseSchema):
    gender: Optional[UserGender] = None
    date_of_birth: Optional[date] = None
    occupation: Optional[str] = Field(None, max_length=255)
    address: Optional[AddressSchema] = None


class UserIdentityProfileResponseSchema(BaseSchema):
    pass


# User Health Profile Schemas
class UserHealthProfileCreateSchema(BaseSchema):
    user_id: UUID
    height_cm: Optional[int] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    activity_level: Optional[ActivityLevel] = None
    curr_condition: Optional[HealthCondition] = None
    health_goal: Optional[HealthGoal] = None


class UserHealthProfileUpdateSchema(BaseSchema):
    height_cm: Optional[int] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    activity_level: Optional[ActivityLevel] = None
    curr_condition: Optional[HealthCondition] = None
    health_goal: Optional[HealthGoal] = None


class UserHealthProfileResponseSchema(BaseSchema):
    pass