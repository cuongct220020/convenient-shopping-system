# /microservices/user-service/app/schemas/__init__.py
"""
This package contains all the Pydantic schemas used for data validation
and serialization in the User Service.

The schemas are organized by resource type.
"""
from .auth import (
    RegisterRequestSchema,
    LoginRequestSchema,
    TokenResponseSchema,
    ChangePasswordRequestSchema,
)
from .otp import (
    SendVerificationOTPRequestSchema,
    VerifyAccountRequestSchema,
    RequestEmailChangeRequestSchema,
    ConfirmEmailChangeRequestSchema,
)
from .profile import (
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
    UserDetailedProfileSchema,
    UserAdminViewSchema,
    UserAdminUpdateSchema,
)
from .group import (
    GroupMemberSchema,
    GroupCreateSchema,
    GroupDetailedSchema,
)
from .response import (
    SuccessResponse,
    TokenDataResponse,
    UserPublicProfileResponse,
    UserCoreInfoResponse,
    UserIdentityProfileResponse,
    UserHealthProfileResponse,
    GroupDetailedResponse,
    GroupMemberResponse,
    UserAdminViewResponse,
    UserAdminViewPaginatedResponse,
    GroupDetailedPaginatedResponse,
    GroupMemberPaginatedResponse,
)

__all__ = [
    # Auth
    "RegisterRequestSchema",
    "LoginRequestSchema",
    "TokenResponseSchema",
    "ChangePasswordRequestSchema",
    # OTP
    "SendVerificationOTPRequestSchema",
    "VerifyAccountRequestSchema",
    "RequestEmailChangeRequestSchema",
    "ConfirmEmailChangeRequestSchema",
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
    "UserDetailedProfileSchema",
    "UserAdminViewSchema",
    "UserAdminUpdateSchema",
    # Group
    "GroupMemberSchema",
    "GroupCreateSchema",
    "GroupDetailedSchema",
    # Responses
    "SuccessResponse",
    "TokenDataResponse",
    "UserPublicProfileResponse",
    "UserCoreInfoResponse",
    "UserIdentityProfileResponse",
    "UserHealthProfileResponse",
    "GroupDetailedResponse",
    "GroupMemberResponse",
    "UserAdminViewResponse",
    "UserAdminViewPaginatedResponse",
    "GroupDetailedPaginatedResponse",
    "GroupMemberPaginatedResponse",
]
