# /microservices/user-service/app/schemas/group.py
from typing import Optional, List
from uuid import UUID
from pydantic import Field
from shopping_shared.schemas.base_schema import BaseSchema
from app.constants import GroupRole
from .user import UserPublicProfileSchema

# --- Group Schemas ---
class GroupMemberSchema(BaseSchema):
    """Schema representing a member within a group."""
    user: UserPublicProfileSchema
    role: GroupRole

class GroupCreateSchema(BaseSchema):
    """Schema for creating a new group."""
    group_name: str = Field(..., min_length=1, max_length=255)
    group_avatar_url: Optional[str] = None

class GroupDetailedSchema(BaseSchema):
    """Detailed schema for a group, including its members."""
    id: UUID
    group_name: str
    group_avatar_url: Optional[str] = None
    creator: Optional[UserPublicProfileSchema] = None
    members: List[GroupMemberSchema] = []
