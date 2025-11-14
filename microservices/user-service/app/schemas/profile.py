# /microservices/user-service/app/schemas/user_bp.py
from datetime import date
from typing import Optional
from pydantic import Field, EmailStr
from shared.shopping_shared.schemas import BaseSchema
from app.constants import UserGender, ActivityLevel, HealthCondition, HealthGoal

# --- Address Schemas ---
class AddressSchema(BaseSchema):
    """Schema for address information."""
    ward: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    city: str = Field(..., max_length=100)
    province: str = Field(..., max_length=100)

# --- User Identity Profile Schemas ---
class UserIdentityProfileSchema(BaseSchema):
    """Schema for user identity profile responses."""
    gender: UserGender = UserGender.OTHER
    date_of_birth: Optional[date] = None
    occupation: Optional[str] = Field(None, max_length=255)
    address: Optional[AddressSchema] = None

class UserIdentityProfileUpdateSchema(BaseSchema):
    """Schema for updating a user's identity profile. All fields are optional."""
    gender: Optional[UserGender] = None
    date_of_birth: Optional[date] = None
    occupation: Optional[str] = Field(None, max_length=255)
    address: Optional[AddressSchema] = None

# --- User Health Profile Schemas ---
class UserHealthProfileSchema(BaseSchema):
    """Schema for user health profile responses."""
    height_cm: Optional[int] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    activity_level: Optional[ActivityLevel] = ActivityLevel.NORMAL
    curr_condition: Optional[HealthCondition] = HealthCondition.NORMAL
    health_goal: Optional[HealthGoal] = HealthGoal.MAINTAIN

class UserHealthProfileUpdateSchema(BaseSchema):
    """Schema for updating a user's health profile. All fields are optional."""
    height_cm: Optional[int] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    activity_level: Optional[ActivityLevel] = None
    curr_condition: Optional[HealthCondition] = None
    health_goal: Optional[HealthGoal] = None
