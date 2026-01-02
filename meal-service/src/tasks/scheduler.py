from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .expire_meals_task import expire_meals

scheduler = AsyncIOScheduler()

def setup_scheduler():
    scheduler.add_job(
        expire_meals,
        trigger=CronTrigger(hour=0, minute=1),
        id="expire_meals",
        name="Expire expired meals",
        replace_existing=True
    )

    return scheduler