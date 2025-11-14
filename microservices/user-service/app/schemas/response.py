# /microservices/user-service/app/schemas/response.py
from typing import List, Optional
from shared.shopping_shared.schemas import GenericResponse, PaginationResponse
from .auth import TokenResponseSchema
from .group import GroupDetailedSchema, GroupMemberSchema
from .profile import UserIdentityProfileSchema, UserHealthProfileSchema
from .user import UserPublicProfileSchema, UserCoreInfoSchema, UserAdminViewSchema

# --- Generic Responses (for 204 No Content) ---
class SuccessResponse(GenericResponse[None]):
    """Standard success response for operations that don't return data."""
    message: str = "Thao tác thành công."

# --- Auth Responses ---
class TokenDataResponse(GenericResponse[TokenResponseSchema]):
    """Response for successful login or token refresh."""
    message: str = "Xác thực thành công."

class UserPublicProfileResponse(GenericResponse[UserPublicProfileSchema]):
    """Response containing a user's public profile."""
    message: str = "Lấy thông tin người dùng thành công."

# --- Profile Responses ---
class UserCoreInfoResponse(GenericResponse[UserCoreInfoSchema]):
    """Response containing the core info of the authenticated user."""
    message: str = "Lấy thông tin người dùng thành công."

class UserIdentityProfileResponse(GenericResponse[UserIdentityProfileSchema]):
    """Response containing a user's identity profile."""
    message: str = "Lấy hồ sơ định danh thành công."

class UserHealthProfileResponse(GenericResponse[UserHealthProfileSchema]):
    """Response containing a user's health profile."""
    message: str = "Lấy hồ sơ sức khỏe thành công."

# --- Group Responses ---
class GroupDetailedResponse(GenericResponse[GroupDetailedSchema]):
    """Response containing detailed information about a group."""
    message: str = "Lấy thông tin nhóm thành công."

class GroupMemberResponse(GenericResponse[GroupMemberSchema]):
    """Response containing information about a group member."""
    message: str = "Thao tác với thành viên nhóm thành công."

# --- Admin Responses ---
class UserAdminViewResponse(GenericResponse[UserAdminViewSchema]):
    """Response for an admin viewing a single user's detailed info."""
    message: str = "Lấy thông tin chi tiết người dùng thành công."

# --- Paginated Responses ---
class UserAdminViewPaginatedResponse(PaginationResponse[UserAdminViewSchema]):
    """Paginated response for listing all users for an admin."""
    message: str = "Lấy danh sách người dùng thành công."

class GroupDetailedPaginatedResponse(PaginationResponse[GroupDetailedSchema]):
    """Paginated response for listing groups."""
    message: str = "Lấy danh sách nhóm thành công."

class GroupMemberPaginatedResponse(PaginationResponse[GroupMemberSchema]):
    """Paginated response for listing group members."""
    message: str = "Lấy danh sách thành viên thành công."
