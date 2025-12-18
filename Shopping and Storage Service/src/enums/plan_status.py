import enum

class PlanStatus(str, enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    def is_active(self):
        return self in {PlanStatus.CREATED, PlanStatus.IN_PROGRESS}