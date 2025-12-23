from typing import Optional
from uuid import UUID
from app.schemas.family_group_schema import FamilyGroupCreateSchema, FamilyGroupUpdateSchema

class FamilyGroupAdminCreateSchema(FamilyGroupCreateSchema):
    """
    Schema for admin to create a group.
    Admin usually creates a group on behalf of a user, so creator_id is required
    to assign the Head Chef role.
    """
    group_name: str
    group_avatar_url: Optional[str] = None
    creator_id: UUID


class FamilyGroupAdminUpdateSchema(FamilyGroupUpdateSchema):
    """
    Schema for admin to update a group.
    Admin can transfer ownership (change Head Chef) by providing a new creator_id.
    """
    group_name: Optional[str] = None
    group_avatar_url: Optional[str] = None
    creator_id: Optional[UUID] = None
