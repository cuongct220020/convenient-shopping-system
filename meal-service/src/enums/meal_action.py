import enum

class MealAction(str, enum.Enum):
    UPSERT = "upsert"
    DELETE = "delete"
    SKIP = "skip"