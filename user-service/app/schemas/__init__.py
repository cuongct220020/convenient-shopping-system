# user-service/app/schemas/__init__.py
"""
This package contains all the Pydantic schemas used for data validation
and serialization in the User Service.

The schemas are organized by resource type.
"""

from .auth_schema import (
    RegisterRequestSchema,
    LoginRequestSchema,
    TokenResponseSchema,
    ResetPasswordRequestSchema,
    ChangePasswordRequestSchema,
    RequestEmailChangeSchema,
    ConfirmEmailChangeRequestSchema
)


from .otp_schema import (
    OTPRequestSchema,
    RegisterVerifyRequestSchema
)

from .user_admin_schema import (
    UserAdminCreateSchema,
    UserAdminViewSchema,
    UserAdminUpdateSchema
)

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
    UserPublicProfileSchema,
    UserInfoUpdateSchema,
    UserCreateSchema,
    UserDetailedProfileSchema
)


from .family_group_schema import (
    FamilyGroupCreateSchema,
    FamilyGroupUpdateSchema,
    FamilyGroupDetailedSchema,
    GroupMembershipSchema,
    GroupMembershipCreateSchema,
    GroupMembershipUpdateSchema,
    AddMemberRequestSchema
)

from .family_group_admin_schema import (
    FamilyGroupAdminCreateSchema,
    FamilyGroupAdminUpdateSchema
)

from .user_tag_schema import (
    UserTagBulkAddSchema,
    UserTagDeleteSchema,
    UserTagUpdateByCategorySchema
)

__all__ = [
    # Auth
    "RegisterRequestSchema",
    "LoginRequestSchema",
    "TokenResponseSchema",
    "ResetPasswordRequestSchema",
    "ChangePasswordRequestSchema",

    # OTP
    "OTPRequestSchema",
    "RegisterVerifyRequestSchema",

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
    "UserPublicProfileSchema",
    "UserInfoUpdateSchema",
    "UserCreateSchema",
    "UserDetailedProfileSchema",
    "UserAdminViewSchema",
    "UserAdminCreateSchema",
    "UserAdminUpdateSchema",
    "RequestEmailChangeSchema",
    "ConfirmEmailChangeRequestSchema",

    # User Tag
    "UserTagBulkAddSchema",
    "UserTagDeleteSchema",
    "UserTagUpdateByCategorySchema",

    # Group
    "FamilyGroupCreateSchema",
    "FamilyGroupUpdateSchema",
    "FamilyGroupDetailedSchema",
    "FamilyGroupAdminCreateSchema",
    "FamilyGroupAdminUpdateSchema",
    "GroupMembershipSchema",
    "GroupMembershipCreateSchema",
    "GroupMembershipUpdateSchema",
    "AddMemberRequestSchema",
]

from .response import (
    TokenDataResponseSchema,
    UserPublicProfileResponseSchema,
    UserInfoResponseSchema,
    UserIdentityProfileResponseSchema,
    UserHealthProfileResponseSchema,
    UserTagsResponseSchema,
    CountResponseSchema,
    FamilyGroupDetailedResponseSchema,
    GroupMembershipListResponseSchema,
    GroupMembershipResponseSchema,
    GroupMembershipDetailedResponseSchema,
    UserAdminViewResponseSchema,
    UserAdminViewListResponseSchema
)

__all__.extend([
    "TokenDataResponseSchema",
    "UserPublicProfileResponseSchema",
    "UserInfoResponseSchema",
    "UserIdentityProfileResponseSchema",
    "UserHealthProfileResponseSchema",
    "UserTagsResponseSchema",
    "CountResponseSchema",
    "FamilyGroupDetailedResponseSchema",
    "GroupMembershipListResponseSchema",
    "GroupMembershipResponseSchema",
    "GroupMembershipDetailedResponseSchema",
    "UserAdminViewResponseSchema",
    "UserAdminViewListResponseSchema"
])