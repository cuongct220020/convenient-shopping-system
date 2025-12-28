from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from tasks.expire_plans_task import expire_plans

scheduler = AsyncIOScheduler()

def setup_scheduler():
    scheduler.add_job(
        expire_plans,
        trigger=CronTrigger(hour="*", minute=1),
        id="expire_plans",
        name="Expire expired shopping plans",
        replace_existing=True
    )

    return scheduler