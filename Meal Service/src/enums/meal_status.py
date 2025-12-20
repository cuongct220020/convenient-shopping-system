import enum

class MealStatus(str, enum.Enum):
    CREATED = "created"
    RESERVED = "reserved"
    BACKORDERED = "backordered"
    DONE = "done"
    CANCELLED = "cancelled"
    EXPIRED = "expired"