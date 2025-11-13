# app/constants/user_constants.py
from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"  # Quản trị viên
    USER = "user"  # Người dùng
    HEAD_CHEF = "head_chef"  # Bếp trưởng (người quản lý chính trong gia đình)
    FAMILY_MEMBER = "family_member"  # Thành viên gia đình


class UserGender(Enum):
    MALE = "male"  # Nam
    FEMALE = "female"  # Nữ
    OTHER = "other"  # Khác

