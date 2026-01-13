from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.database import get_db
from core.messaging import kafka_manager
from models.storage import Storage, StorableUnit
from shopping_shared.messaging.kafka_topics import NOTIFICATION_TOPIC
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("Expiration Units Task")


async def publish_expiration_notifications() -> None:
    db: Session = next(get_db())
    try:
        today = date.today()
        expiring_soon_day = today + timedelta(days=3)

        stmt = (
            select(
                Storage.group_id,
                Storage.storage_id,
                Storage.storage_name,
                StorableUnit.unit_name,
                StorableUnit.expiration_date,
            )
            .join(Storage, StorableUnit.storage_id == Storage.storage_id)
            .where(StorableUnit.expiration_date.in_([today, expiring_soon_day]))
        )
        rows = db.execute(stmt).all()

        expired_today: Dict[str, List[Tuple[str, str, date]]] = defaultdict(list)
        expiring_soon: Dict[str, List[Tuple[str, str, date]]] = defaultdict(list)

        for group_id, storage_id, storage_name, unit_name, expiration_date in rows:
            if expiration_date is None:
                continue

            storage_name_final = storage_name or f"Storage #{storage_id}"

            if expiration_date == today:
                expired_today[str(group_id)].append((storage_name_final, unit_name, expiration_date))
            elif expiration_date == expiring_soon_day:
                expiring_soon[str(group_id)].append((storage_name_final, unit_name, expiration_date))

        for group_id, items in expired_today.items():
            for storage_name, unit_name, exp_date in items:
                try:
                    await kafka_manager.send_message(
                        topic=NOTIFICATION_TOPIC,
                        value={
                            "event_type": "food_expired",
                            "group_id": group_id,
                            "receiver_is_head_chef": False,
                            "data": {
                                "unit_name": unit_name,
                                "storage_name": storage_name,
                            }
                        },
                        key=f"{group_id}-food-expired",
                        wait=True,
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to publish food_expired for group={group_id}, unit={unit_name}: {e}",
                        exc_info=True,
                    )

        for group_id, items in expiring_soon.items():
            for storage_name, unit_name, exp_date in items:
                try:
                    await kafka_manager.send_message(
                        topic=NOTIFICATION_TOPIC,
                        value={
                            "event_type": "food_expiring_soon",
                            "group_id": group_id,
                            "receiver_is_head_chef": False,
                            "data": {
                                "unit_name": unit_name,
                                "storage_name": storage_name,
                                "expiration_date": exp_date.strftime("%d/%m/%Y"),
                            }
                        },
                        key=f"{group_id}-food-expiring-soon",
                        wait=True,
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to publish food_expiring_soon for group={group_id}, unit={unit_name}: {e}",
                        exc_info=True,
                    )

    finally:
        db.close()


