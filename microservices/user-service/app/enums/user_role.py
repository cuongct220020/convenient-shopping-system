# app/constants/user_role_constants.py
from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    HEAD_CHEF = "head_chef"
    FAMILY_MEMBER = "family_member"
