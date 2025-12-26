from shared.shopping_shared.messaging.kafka_manager import kafka_manager
from shared.shopping_shared.messaging.topics import RECIPE_EVENTS_TOPIC
from messaging.handlers.recipe_handler import (
    handle_recipe_upsert,
    handle_recipe_deleted
)


async def consume_recipe_events():
    consumer = kafka_manager.create_consumer(
        RECIPE_EVENTS_TOPIC,
        group_id="recipe_service_recipe_group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            if event.get("event_type") == "recipe_created" or event.get("event_type") == "recipe_updated":
                await handle_recipe_upsert(event.get("data"))
            elif event.get("event_type") == "recipe_deleted":
                await handle_recipe_deleted(event.get("data"))
    finally:
        await consumer.stop()

