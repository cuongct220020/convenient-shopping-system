from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from tasks.expire_plans_task import expire_plans
from tasks.expire_units_task import publish_expiration_notifications
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Scheduler")

scheduler = AsyncIOScheduler()

def setup_scheduler():
    scheduler.add_job(
        expire_plans,
        trigger=CronTrigger(hour="*", minute=1),
        id="expire_plans",
        name="Expire expired shopping plans",
        replace_existing=True
    )

    scheduler.add_job(
        publish_expiration_notifications,
        trigger=CronTrigger(hour=0, minute=0),
        id="publish_expiration_notifications",
        name="Publish expiration notifications (00:00)",
        replace_existing=True
    )

    logger.info("Scheduler setup completed with 2 jobs")
    return scheduler