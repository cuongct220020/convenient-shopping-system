from shared.shopping_shared.messaging.kafka_manager import kafka_manager
from shared.shopping_shared.messaging.topics import INGREDIENT_EVENTS_TOPIC
from messaging.handlers.ingredient_handler import (
    handle_ingredient_upsert,
    handle_ingredient_deleted
)


async def consume_ingredient_events():
    consumer = kafka_manager.create_consumer(
        INGREDIENT_EVENTS_TOPIC,
        group_id="recipe_service_ingredient_group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            if event.get("event_type") == "ingredient_created" or event.get("event_type") == "ingredient_updated":
                await handle_ingredient_upsert(event.get("data"))
            elif event.get("event_type") == "ingredient_deleted":
                await handle_ingredient_deleted(event.get("data"))
    finally:
        await consumer.stop()
