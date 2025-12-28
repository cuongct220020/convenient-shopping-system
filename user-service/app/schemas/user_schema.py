# user-service/app/schemas/user_schema.py
from typing import Optional
from uuid import UUID

from pydantic import Field, EmailStr, SecretStr
from shopping_shared.schemas.base_schema import BaseSchema

# User Base Schema
class UserCoreInfoSchema(BaseSchema):
    user_id: UUID = Field(..., description="The ID of the user", validation_alias="id")
    username: str = Field(
        ...,
        description="The username of the user",
        min_length=3,
        max_length=50
    )
    email: EmailStr = Field(
        ...,
        description="The email of the user",
        min_length=3,
        max_length=255
    )
    phone_num: Optional[str] = Field(
        None,
        description="The phone number of the user",
        min_length=3,
        max_length=15
    )
    first_name: Optional[str] = Field(
        None,
        description="The first name of the user",
        min_length=1,
        max_length=100
    )
    last_name: Optional[str] = Field(
        None,
        description="The last name of the user",
        min_length=1,
        max_length=100
    )
    avatar_url: Optional[str] = Field(
        None,
        description="The avatar of the user",
    )



class UserInfoUpdateSchema(BaseSchema):
    """Schema for update user core information."""
    username: Optional[str] = Field(
        default=None,
        description="The username of the user",
        min_length=3,
    )
    first_name: Optional[str] = Field(
        None,
        description="The first name of the user",
        min_length=1,
        max_length=255
    )
    last_name: Optional[str] = Field(
        None,
        description="The last name of the user",
        min_length=1,
        max_length=255
    )
    phone_num: Optional[str] = Field(
        None,
        description="The phone number of the user",
        min_length=3,
        max_length=15
    )
    avatar_url: Optional[str] = Field(
        None,
        description="The avatar of the user",
        min_length=1,
        max_length=255
    )


class UserCreateSchema(BaseSchema):
    """Schema for creating a new user, used internally."""
    username: str = Field(
        ...,
        description="The username of the user",
        examples=["username1"],
        min_length=3,
        max_length=50
    )
    email: EmailStr = Field(
        ...,
        description="The email of the user",
        examples=["user1@example.com"],
        min_length=3,
        max_length=255
    )
    password: SecretStr = Field(
        ...,
        description="The password of the user",
        examples=["password1"],
    )
    first_name: Optional[str] = Field(
        None,
        description="The first name of the user",
        examples=["user1"],
        min_length=1,
        max_length=50,
    )
    last_name: Optional[str] = Field(
        None,
        description="The last name of the user",
        examples=["user1"],
        min_length=1,
        max_length=50
    )
    phone_num: Optional[str] = Field(
        None,
        description="The phone number of the user",
        examples=["0813090204"],
        min_length=3,
        max_length=15
    )
    is_active: bool = False
