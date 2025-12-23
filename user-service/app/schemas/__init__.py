# /microservices/user-service/app/schemas/__init__.py
"""
This package contains all the Pydantic schemas used for data validation
and serialization in the User Service.

The schemas are organized by resource type.
"""

from .auth_schema import (
    RegisterRequestSchema,
    LoginRequestSchema,
    AccessTokenSchema,
    ResetPasswordRequestSchema,
)


from .otp_schema import (
    OTPRequestSchema,
    OTPVerifyRequestSchema
)

from .user_profile_schema import (
    # Identity Profile
    UserIdentityProfileCreateSchema,
    UserIdentityProfileUpdateSchema,
    # Health Profile
    UserHealthProfileCreateSchema,
    UserHealthProfileUpdateSchema,
)

from .user_schema import (
    UserInfoSchema,
    UserInfoUpdateSchema,
    UserCreateSchema,
    UserAdminCreateSchema,
    UserDetailedProfileSchema,
    UserAdminViewSchema,
    UserAdminUpdateSchema,
)
from .family_group_schema import (
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

    # Profile - Identity
    "AddressSchema",
    "UserIdentityProfileCreateSchema",
    "UserIdentityProfileResponseSchema",
    "UserIdentityProfileUpdateSchema",

    # Profile - Health
    "UserHealthProfileCreateSchema",
    "UserHealthProfileResponseSchema",
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
