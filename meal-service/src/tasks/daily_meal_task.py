import asyncio
from collections import defaultdict
from datetime import date
from typing import Dict, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.database import get_db
from enums.meal_status import MealStatus
from enums.meal_type import MealType
from core.messaging import kafka_manager
from models.meal import Meal
from shopping_shared.messaging.kafka_topics import NOTIFICATION_TOPIC
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("Daily Meal Task")


def fetch_today_meals_grouped() -> Dict[str, Dict[str, List[str]]]:
    db = next(get_db())
    today = date.today()
    try:
        meals = db.execute(
            select(Meal)
            .where(Meal.date == today, Meal.meal_status == MealStatus.CREATED)
            .options(selectinload(Meal.recipe_list))
        ).scalars().all()

        grouped: Dict[str, Dict[str, List[str]]] = defaultdict(
            lambda: {"breakfast": [], "lunch": [], "dinner": []}
        )

        for meal in meals:
            gid = str(meal.group_id)
            recipes = [r.recipe_name for r in (meal.recipe_list or [])]
            if meal.meal_type == MealType.BREAKFAST:
                grouped[gid]["breakfast"] = recipes
            elif meal.meal_type == MealType.LUNCH:
                grouped[gid]["lunch"] = recipes
            elif meal.meal_type == MealType.DINNER:
                grouped[gid]["dinner"] = recipes

        return dict(grouped)
    finally:
        db.close()


async def publish_daily_meals() -> None:
    grouped = fetch_today_meals_grouped()
    if not grouped:
        logger.info("No meals found for today. Skipping daily_meal publish.")
        return

    for group_id, meals in grouped.items():
        payload = {
            "event_type": "daily_meal",
            "group_id": group_id,
            "receiver_is_head_chef": True,
            "data": {
                "breakfast": meals.get("breakfast", []) or [],
                "lunch": meals.get("lunch", []) or [],
                "dinner": meals.get("dinner", []) or [],
            },
        }

        try:
            await kafka_manager.send_message(
                topic=NOTIFICATION_TOPIC,
                value=payload,
                key=f"{group_id}-meal",
                wait=True,
            )
            logger.info(f"Published daily_meal event: group_id={group_id}")
        except Exception as e:
            logger.error(f"Failed to publish daily_meal for group {group_id}: {e}", exc_info=True)


