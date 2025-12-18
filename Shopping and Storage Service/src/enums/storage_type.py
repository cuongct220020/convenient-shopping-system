import enum

class StorageType(str, enum.Enum):
    FRIDGE = "fridge"
    FREEZER = "freezer"
    PANTRY = "pantry"
    BULK_STORAGE = "bulk_storage"