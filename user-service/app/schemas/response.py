# user-service/app/schemas/response.py
from pydantic import BaseModel, Field
from typing import Optional, List
from shopping_shared.sanic.schemas import DocGenericResponse
from .auth_schema import TokenResponseSchema
from .user_schema import UserPublicProfileSchema, UserInfoSchema
from .user_profile_schema import UserIdentityProfileSchema, UserHealthProfileSchema
from .user_tag_schema import UserTagsByCategorySchema
from .family_group_schema import (
    FamilyGroupDetailedSchema,
    GroupMembershipSchema,
    GroupMembershipDetailedSchema
)
from .user_admin_schema import UserAdminViewSchema

class TokenDataResponseSchema(DocGenericResponse):
    data: Optional[TokenResponseSchema] = None

class UserPublicProfileResponseSchema(DocGenericResponse):
    data: Optional[UserPublicProfileSchema] = None

class UserInfoResponseSchema(DocGenericResponse):
    data: Optional[UserInfoSchema] = None

class UserIdentityProfileResponseSchema(DocGenericResponse):
    data: Optional[UserIdentityProfileSchema] = None

class UserHealthProfileResponseSchema(DocGenericResponse):
    data: Optional[UserHealthProfileSchema] = None

class UserTagsResponseSchema(DocGenericResponse):
    data: Optional[UserTagsByCategorySchema] = None

class CountResponseData(BaseModel):
    count: int = Field(..., alias="count")

class CountResponseSchema(DocGenericResponse):
    data: Optional[CountResponseData] = None

# --- Group Schemas ---
class FamilyGroupDetailedResponseSchema(DocGenericResponse):
    data: Optional[FamilyGroupDetailedSchema] = None

class GroupMembershipListResponseSchema(DocGenericResponse):
    data: Optional[List[GroupMembershipSchema]] = None
    
class GroupMembershipResponseSchema(DocGenericResponse):
    data: Optional[GroupMembershipSchema] = None
    
class GroupMembershipDetailedResponseSchema(DocGenericResponse):
    data: Optional[GroupMembershipDetailedSchema] = None

# --- Admin Schemas ---
class UserAdminViewResponseSchema(DocGenericResponse):
    data: Optional[UserAdminViewSchema] = None

class UserAdminViewListResponseSchema(DocGenericResponse):
    data: Optional[List[UserAdminViewSchema]] = None
