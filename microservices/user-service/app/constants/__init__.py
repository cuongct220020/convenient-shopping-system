# app/constants/__init__.py
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
)

__all__ = [
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
]
