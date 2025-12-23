# microservices/user-service/app/enums/__init__.py
from .auth import OtpAction
from .tags import (
    AgeTag,
    AllergyTag,
    MedicalConditionTag,
    SpecialDietTag,
    TastePreferenceTag,
)
from .user import (
    ActivityLevel,
    HealthCondition,
    HealthGoal,
    UserGender,
    UserRole,
    GroupRole,
)

__all__ = [
    # Auth
    "OtpAction",
    # Tags
    "AgeTag",
    "AllergyTag",
    "MedicalConditionTag",
    "SpecialDietTag",
    "TastePreferenceTag",
    # User
    "ActivityLevel",
    "HealthCondition",
    "HealthGoal",
    "UserGender",
    "UserRole",
    "GroupRole",
]
