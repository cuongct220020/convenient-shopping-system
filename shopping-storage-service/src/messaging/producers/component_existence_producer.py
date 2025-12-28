from typing import Sequence
from core.messaging import kafka_manager
from shared.shopping_shared.messaging.topics import COMPONENT_EXISTENCE_TOPIC


async def publish_component_existence_update(group_id: int, unit_names: Sequence[str]):
    payload = {
        "event_type": "update_component_existence",
        "data": {
            "group_id": group_id,
            "unit_names": unit_names
        }
    }

    producer = await kafka_manager.get_producer()
    await producer.send(COMPONENT_EXISTENCE_TOPIC, value=payload)

