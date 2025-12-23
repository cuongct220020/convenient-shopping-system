# user-service/app/enums/user_schema.py
from enum import Enum


class UserRole(str, Enum):
    """Enum for system-level user roles."""
    ADMIN = "admin"
    USER = "user"


class GroupRole(str, Enum):
    """Enum for user roles within a family groups."""
    HEAD_CHEF = "head_chef"
    MEMBER = "member"


class UserGender(str, Enum):
    """Enum for user genders."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ActivityLevel(str, Enum):
    """Enum for user activity levels."""
    SEDENTARY = "sedentary"  # Ít vận động; hệ số 1.2; ngồi nhiều, không tập
    LIGHT = "light"  # Vận động nhẹ; hệ số 1.375; 1-3 buổi/tuần
    MODERATE = "moderate"  # Vận động vừa; hệ số 1.5; 3-5 buổi/tuần
    ACTIVE = "active"  # Năng động (tập nặng); hệ số 1.725; 6-7 buổi/tuần.
    VERY_ACTIVE = "very_active"  # Rất năng động (tập rất nặng); hệ số 1.9; Lao động nặng, 2 lần tập/ngày


class HealthCondition(str, Enum):
    """Enum for user health conditions."""
    NORMAL = "normal"
    PREGNANT = "pregnant"  # Mang thai
    INJURED = "injured"  # Chấn thương


class HealthGoal(str, Enum):
    """Enum for user health goals."""
    LOSE_WEIGHT = "lose_weight"  # Giảm cân
    MAINTAIN = "maintain"  # Duy trì
    GAIN_WEIGHT = "gain_weight"  # Tăng cân
