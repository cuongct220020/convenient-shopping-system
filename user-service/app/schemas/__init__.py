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
    ChangePasswordRequestSchema
)


from .otp_schema import (
    OTPRequestSchema,
    OTPVerifyRequestSchema
)

from .user_admin_schema import UserAdminCreateSchema

from .user_profile_schema import (
    AddressSchema,

    # Identity Profile
    UserIdentityProfileSchema,
    UserIdentityProfileCreateSchema,
    UserIdentityProfileUpdateSchema,

    # Health Profile
    UserHealthProfileSchema,
    UserHealthProfileCreateSchema,
    UserHealthProfileUpdateSchema,
)

from .user_schema import (
    UserInfoSchema,
    UserInfoUpdateSchema,
    UserCreateSchema,
    UserDetailedProfileSchema,
    UserAdminViewSchema,
    UserAdminUpdateSchema,
    RequestEmailChangeSchema,
    ConfirmEmailChangeSchema
)



from .family_group_schema import (
    FamilyGroupMemberSchema,
    FamilyGroupCreateSchema,
    FamilyGroupUpdateSchema,
    FamilyGroupDetailedSchema,
    AddMemberRequestSchema,
    UpdateMemberRoleRequestSchema
)

from .family_group_admin_schema import (
    FamilyGroupAdminCreateSchema,
    FamilyGroupAdminUpdateSchema
)

__all__ = [
    # Auth
    "RegisterRequestSchema",
    "LoginRequestSchema",
    "AccessTokenSchema",
    "ResetPasswordRequestSchema",
    "ChangePasswordRequestSchema",

    # OTP
    "OTPRequestSchema",
    "OTPVerifyRequestSchema",

    # Profile - Identity
    "AddressSchema",
    "UserIdentityProfileSchema",
    "UserIdentityProfileCreateSchema",
    "UserIdentityProfileUpdateSchema",

    # Profile - Health
    "UserHealthProfileSchema",
    "UserHealthProfileCreateSchema",
    "UserHealthProfileUpdateSchema",

    # User
    "UserInfoSchema",
    "UserInfoUpdateSchema",
    "UserCreateSchema",
    "UserDetailedProfileSchema",
    "UserAdminViewSchema",
    "UserAdminCreateSchema",
    "UserAdminUpdateSchema",
    "RequestEmailChangeSchema",
    "ConfirmEmailChangeSchema",

    # Group
    "FamilyGroupMemberSchema",
    "FamilyGroupCreateSchema",
    "FamilyGroupUpdateSchema",
    "FamilyGroupDetailedSchema",
    "FamilyGroupAdminCreateSchema",
    "FamilyGroupAdminUpdateSchema",
    "AddMemberRequestSchema",
    "UpdateMemberRoleRequestSchema"
]
