# app/constants/user.py
import enum


class UserRole(str, enum.Enum):
    """Enum for system-level user roles."""
    ADMIN = "admin"
    USER = "user"


class GroupRole(str, enum.Enum):
    """Enum for user roles within a family groups."""
    HEAD_CHEF = "head_chef"
    MEMBER = "member"


class UserGender(str, enum.Enum):
    """Enum for user genders."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ActivityLevel(str, enum.Enum):
    """Enum for user activity levels."""
    SEDENTARY = "sedentary"  # Ít vận động
    LIGHT = "light"  # Vận động nhẹ
    MODERATE = "moderate"  # Vận động vừa
    ACTIVE = "active"  # Năng động
    VERY_ACTIVE = "very_active"  # Rất năng động


class HealthCondition(str, enum.Enum):
    """Enum for user health conditions."""
    NORMAL = "normal"
    PREGNANT = "pregnant"  # Mang thai
    INJURED = "injured"  # Chấn thương


class HealthGoal(str, enum.Enum):
    """Enum for user health goals."""
    LOSE_WEIGHT = "lose_weight"  # Giảm cân
    MAINTAIN = "maintain"  # Duy trì
    GAIN_WEIGHT = "gain_weight"  # Tăng cân
