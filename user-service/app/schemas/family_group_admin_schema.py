from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.family_group_schema import FamilyGroupCreateSchema, FamilyGroupUpdateSchema


class FamilyGroupAdminCreateSchema(FamilyGroupCreateSchema):
    """
    Schema for admin to create a group.
    Admin usually creates a group on behalf of a user, so creator_id is required
    to assign the Head Chef role.
    """
    group_name: str = Field(..., description="The name of the family group.", min_length=1, max_length=255)
    group_avatar_url: Optional[str] = Field(None)
    creator_id: UUID = Field(None, description="The ID of the creator of the family group.")


class FamilyGroupAdminUpdateSchema(FamilyGroupUpdateSchema):
    """
    Schema for admin to update a group.
    Admin can transfer ownership (change Head Chef) by providing a new creator_id.
    """
    group_name: Optional[str] = Field(None, description="The name of the family group.", min_length=1, max_length=255)
    group_avatar_url: Optional[str] = Field(None)
    creator_id: Optional[UUID] = Field(None, description="The ID of the creator of the family group.")
