from datetime import datetime
from sqlalchemy import select
from enums.plan_status import PlanStatus
from models.shopping_plan import ShoppingPlan
from database import get_db

async def expire_plans():
    db = next(get_db())
    try:
        now = datetime.now()
        expired_count = 0
        
        with db.begin():
            plans = db.execute(
                select(ShoppingPlan)
                .where(
                    ShoppingPlan.plan_status.in_([PlanStatus.CREATED, PlanStatus.IN_PROGRESS]),
                    ShoppingPlan.deadline < now
                )
                .with_for_update()
            ).scalars().all()
            
            for plan in plans:
                plan.plan_status = PlanStatus.EXPIRED
                expired_count += 1
    except:
        db.rollback()
        raise
    finally:
        db.close()

