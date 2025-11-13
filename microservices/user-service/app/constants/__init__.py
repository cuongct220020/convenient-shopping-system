# app/constants/__init__.py
from .auth import OTPAction
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
    "OTPAction",
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
