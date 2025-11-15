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
    ChangePasswordRequestSchema,
)
from .otp import (
    SendVerificationOTPRequestSchema,
    VerifyAccountRequestSchema,
    RequestEmailChangeRequestSchema,
    ConfirmEmailChangeRequestSchema,
    ResetPasswordRequestSchema,
)
from .user_profile import (
    AddressSchema,
    UserIdentityProfileSchema,
    UserIdentityProfileUpdateSchema,
    UserHealthProfileSchema,
    UserHealthProfileUpdateSchema,
)
from .user import (
    UserPublicProfileSchema,
    UserCoreInfoSchema,
    UserUpdateSchema,
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
    "ChangePasswordRequestSchema",

    # OTP
    "SendVerificationOTPRequestSchema",
    "VerifyAccountRequestSchema",
    "RequestEmailChangeRequestSchema",
    "ConfirmEmailChangeRequestSchema",
    "ResetPasswordRequestSchema",

    # Profile
    "AddressSchema",
    "UserIdentityProfileSchema",
    "UserIdentityProfileUpdateSchema",
    "UserHealthProfileSchema",
    "UserHealthProfileUpdateSchema",

    # User
    "UserPublicProfileSchema",
    "UserCoreInfoSchema",
    "UserUpdateSchema",
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
