# user-service/app/enums/user_schema.py
from enum import Enum


class SystemRole(str, Enum):
    """Enum for system-level user roles."""
    ADMIN = "admin"
    USER = "user"


class GroupRole(str, Enum):
    """
    Enum for user roles within a family group.

    HEAD_CHEF: Người tạo nhóm và có quyền cao nhất trong nhóm.
               - Thêm/xóa thành viên
               - Cập nhật thông tin nhóm
               - Xóa nhóm
               - Chuyển quyền HEAD_CHEF cho thành viên khác

    MEMBER: Thành viên thông thường.
            - Xem thông tin nhóm
            - Xem profile các thành viên khác
            - Rời nhóm
    """
    HEAD_CHEF = "head_chef"  # Chủ nhóm - quyền cao nhất
    MEMBER = "member"        # Thành viên thông thường


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
