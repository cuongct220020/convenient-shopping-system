from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .expire_meals_task import expire_meals
from .daily_meal_task import publish_daily_meals

scheduler = AsyncIOScheduler()

def setup_scheduler():
    scheduler.add_job(
        expire_meals,
        trigger=CronTrigger(hour=0, minute=1),
        id="expire_meals",
        name="Expire expired meals",
        replace_existing=True
    )

    scheduler.add_job(
        publish_daily_meals,
        trigger=CronTrigger(hour=6, minute=0),
        id="publish_daily_meals",
        name="Publish daily meal notifications (06:00)",
        replace_existing=True
    )

    return scheduler