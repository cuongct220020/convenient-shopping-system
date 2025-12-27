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

class TokenDataResponseSchema(DocGenericResponse[TokenResponseSchema]):
    pass

class UserPublicProfileResponseSchema(DocGenericResponse[UserPublicProfileSchema]):
    pass

class UserInfoResponseSchema(DocGenericResponse[UserInfoSchema]):
    pass

class UserIdentityProfileResponseSchema(DocGenericResponse[UserIdentityProfileSchema]):
    pass

class UserHealthProfileResponseSchema(DocGenericResponse[UserHealthProfileSchema]):
    pass

class UserTagsResponseSchema(DocGenericResponse[UserTagsByCategorySchema]):
    pass

class CountResponseData(BaseModel):
    count: int = Field(..., alias="count")

class CountResponseSchema(DocGenericResponse[CountResponseData]):
    pass

# --- Group Schemas ---
class FamilyGroupDetailedResponseSchema(DocGenericResponse[FamilyGroupDetailedSchema]):
    pass

class GroupMembershipListResponseSchema(DocGenericResponse[List[GroupMembershipSchema]]):
    pass
    
class GroupMembershipResponseSchema(DocGenericResponse[GroupMembershipSchema]):
    pass
    
class GroupMembershipDetailedResponseSchema(DocGenericResponse[GroupMembershipDetailedSchema]):
    pass

# --- Admin Schemas ---
class UserAdminViewResponseSchema(DocGenericResponse[UserAdminViewSchema]):
    pass

class UserAdminViewListResponseSchema(DocGenericResponse[List[UserAdminViewSchema]]):
    pass
