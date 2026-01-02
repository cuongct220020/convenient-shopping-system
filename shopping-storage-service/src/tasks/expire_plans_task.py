from datetime import datetime
from sqlalchemy import update
from enums.plan_status import PlanStatus
from models.shopping_plan import ShoppingPlan
from core.database import get_db

def expire_plans():
    db = next(get_db())
    now = datetime.now()

    with db.begin():
        result = db.execute(
            update(ShoppingPlan)
            .where(
                ShoppingPlan.plan_status.in_([PlanStatus.CREATED, PlanStatus.IN_PROGRESS]),
                ShoppingPlan.deadline < now
            )
            .values(plan_status=PlanStatus.EXPIRED)
        )

    db.close()