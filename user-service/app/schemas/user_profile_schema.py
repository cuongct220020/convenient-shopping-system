# user-service/app/schemas/user_bp.py
from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import Field
from sanic_ext.extensions.openapi import openapi

from app.enums import UserGender, ActivityLevel, HealthCondition, HealthGoal
from app.schemas.user_schema import UserCoreInfoSchema

from shopping_shared.schemas.base_schema import BaseSchema

@openapi.component
class AddressSchema(BaseSchema):
    ward: Optional[str] = Field(
        None,
        description="The ward of the user",
        min_length=1,
        max_length=100
    )
    district: Optional[str] = Field(
        None,
        description="The district of the user",
        min_length=1,
        max_length=100)
    city: Optional[str] = Field(
        None,
        description="The city of the user",
        min_length=1,
        max_length=100
    )
    province: Optional[str] = Field(
        None,
        description="The province of the user",
        min_length=1,
        max_length=100
    )


# User Identity Profile Schemas
@openapi.component
class UserIdentityProfileSchema(BaseSchema):
    user_id: UUID = Field(
        ...,
        description="The ID of the user",
    )
    gender: UserGender = Field(
        ...,
        description="The gender of the user"
    )
    date_of_birth: Optional[date] = Field(
        None,
        description="The date of birth of the user"
    )
    occupation: Optional[str] = Field(
        None,
        description="The occupation of the user"
    )
    address: Optional[AddressSchema] = Field(
        None,
        description="The address of the user"
    )


@openapi.component
class UserIdentityProfileCreateSchema(UserIdentityProfileSchema):
    user_id: Optional[UUID] = Field(None, description="The ID of the user")


@openapi.component
class UserIdentityProfileUpdateSchema(BaseSchema):
    gender: Optional[UserGender] = Field(None)
    date_of_birth: Optional[date] = Field(None)
    occupation: Optional[str] = Field(None, max_length=255)
    address: Optional[AddressSchema] = Field(None)


# User Health Profile Schemas
@openapi.component
class UserHealthProfileSchema(BaseSchema):
    user_id: UUID = Field(
        None,
        description="The ID of the user"
    )
    height_cm: Optional[int] = Field(
        None,
        description="The height of the user",
        gt=0,
        lt=300
    )
    weight_kg: Optional[float] = Field(
        None,
        description="The weight of the user",
        gt=0,
        lt=1000
    )
    activity_level: Optional[ActivityLevel] = Field(
        None,
        description="The activity level of the user"
    )
    curr_condition: Optional[HealthCondition] = Field(
        None,
        description="The current condition of the user"
    )
    health_goal: Optional[HealthGoal] = Field(
        None,
        description="The health goal of the user"
    )


@openapi.component
class UserHealthProfileCreateSchema(UserHealthProfileSchema):
    user_id: Optional[UUID] = Field(None, description="The ID of the user")


@openapi.component
class UserHealthProfileUpdateSchema(BaseSchema):
    height_cm: Optional[int] = Field(
        None,
        description="The height of the user",
        examples=["170"],
        gt=0,
        lt=300
    )
    weight_kg: Optional[float] = Field(
        None,
        description="The weight of the user",
        examples=["70"],
        gt=0,
        lt=1000
    )
    activity_level: Optional[ActivityLevel] = Field(
        None,
        description="The activity level of the user"
    )
    curr_condition: Optional[HealthCondition] = Field(
        None,
        description="The current condition of the user"
    )
    health_goal: Optional[HealthGoal] = Field(
        None,
        description="The health goal of the user"
    )

@openapi.component
class UserDetailedProfileSchema(UserCoreInfoSchema):
    """Full user profile including identity and health info."""
    identity_profile: Optional[UserIdentityProfileSchema] = Field(
        None,
        description="The identity profile of the user"
    )
    health_profile: Optional[UserHealthProfileSchema] = Field(
        None,
        description="The health profile of the user"
    )