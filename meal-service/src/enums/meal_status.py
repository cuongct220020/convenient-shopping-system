import enum

class MealStatus(str, enum.Enum):
    CREATED = "created"
    DONE = "done"
    CANCELLED = "cancelled"
    EXPIRED = "expired"