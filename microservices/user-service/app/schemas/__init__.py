# /microservices/user-service/app/schemas/__init__.py
"""
This package contains all the Pydantic schemas used for data validation
and serialization in the User Service.

The schemas are organized by resource type.
"""
from .auth import (
    RegisterRequestSchema,
    LoginRequestSchema,
    AccessTokenSchema,
    ResetPasswordRequestSchema,
)
from .otp import (
    OTPRequestSchema,
    OTPVerifyRequestSchema
)

from .user_profile import (
    AddressSchema,
    UserIdentityProfileSchema,
    UserIdentityProfileUpdateSchema,
    UserHealthProfileSchema,
    UserHealthProfileUpdateSchema,
)
from .user import (
    UserInfoSchema,
    UserInfoUpdateSchema,
    UserCreateSchema,
    UserAdminCreateSchema,
    UserDetailedProfileSchema,
    UserAdminViewSchema,
    UserAdminUpdateSchema,
)
from .family_group import (
    FamilyGroupMemberSchema,
    FamilyGroupCreateSchema,
    FamilyGroupUpdateSchema,
    FamilyGroupDetailedSchema
)

__all__ = [
    # Auth
    "RegisterRequestSchema",
    "LoginRequestSchema",
    "AccessTokenSchema",
    "ResetPasswordRequestSchema",

    # OTP
    "OTPRequestSchema",
    "OTPVerifyRequestSchema",

    # Profile
    "AddressSchema",
    "UserIdentityProfileSchema",
    "UserIdentityProfileUpdateSchema",
    "UserHealthProfileSchema",
    "UserHealthProfileUpdateSchema",

    # User
    "UserInfoSchema",
    "UserInfoUpdateSchema",
    "UserCreateSchema",
    "UserAdminCreateSchema",
    "UserDetailedProfileSchema",
    "UserAdminViewSchema",
    "UserAdminUpdateSchema",

    # Group
    "FamilyGroupMemberSchema",
    "FamilyGroupCreateSchema",
    "FamilyGroupUpdateSchema",
    "FamilyGroupDetailedSchema"
]
