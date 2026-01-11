from datetime import datetime
from sqlalchemy import update
from enums.plan_status import PlanStatus
from models.shopping_plan import ShoppingPlan
from core.database import get_db
from core.messaging import kafka_manager
from shopping_shared.messaging.kafka_topics import NOTIFICATION_TOPIC
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Expire Plans Task")


async def expire_plans():
    db = next(get_db())
    now = datetime.now()

    with db.begin():
        stmt = (
            update(ShoppingPlan)
            .where(
                ShoppingPlan.plan_status.in_([PlanStatus.CREATED, PlanStatus.IN_PROGRESS]),
                ShoppingPlan.deadline < now
            )
            .values(plan_status=PlanStatus.EXPIRED)
            .returning(
                ShoppingPlan.plan_id,
                ShoppingPlan.group_id,
                ShoppingPlan.assigner_id,
                ShoppingPlan.deadline,
            )
        )
        expired_plans = list(db.execute(stmt).all())

    for plan_id, group_id, assigner_id, deadline in expired_plans:
        try:
            await kafka_manager.send_message(
                topic=NOTIFICATION_TOPIC,
                value={
                    "event_type": "plan_expired",
                    "group_id": str(group_id),
                    "receivers": [str(assigner_id)],
                    "data": {
                        "plan_id": plan_id,
                        "deadline": deadline.isoformat(),
                    }
                },
                key=f"{plan_id}-plan",
                wait=True,
            )
        except Exception as e:
            logger.error(f"Failed to publish plan_expired for plan_id={plan_id}: {e}", exc_info=True)

    db.close()