# user-service/app/enums/user_schema.py
from enum import Enum
from sanic_ext import openapi


@openapi.component
class SystemRole(str, Enum):
    """Enum for system-level user roles."""
    ADMIN = "admin"
    USER = "user"


@openapi.component
class GroupRole(str, Enum):
    HEAD_CHEF = "head_chef"  # Chủ nhóm - quyền cao nhất
    MEMBER = "member"        # Thành viên thông thường


@openapi.component
class UserGender(str, Enum):
    """Enum for user genders."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


@openapi.component
class ActivityLevel(str, Enum):
    """Enum for user activity levels."""
    SEDENTARY = "sedentary"  # Ít vận động; hệ số 1.2; ngồi nhiều, không tập
    LIGHT = "light"  # Vận động nhẹ; hệ số 1.375; 1-3 buổi/tuần
    MODERATE = "moderate"  # Vận động vừa; hệ số 1.5; 3-5 buổi/tuần
    ACTIVE = "active"  # Năng động (tập nặng); hệ số 1.725; 6-7 buổi/tuần.
    VERY_ACTIVE = "very_active"  # Rất năng động (tập rất nặng); hệ số 1.9; Lao động nặng, 2 lần tập/ngày


@openapi.component
class HealthCondition(str, Enum):
    """Enum for user health conditions."""
    NORMAL = "normal"
    PREGNANT = "pregnant"  # Mang thai
    INJURED = "injured"  # Chấn thương


@openapi.component
class HealthGoal(str, Enum):
    """Enum for user health goals."""
    LOSE_WEIGHT = "lose_weight"  # Giảm cân
    MAINTAIN = "maintain"  # Duy trì
    GAIN_WEIGHT = "gain_weight"  # Tăng cân
