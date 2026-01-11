from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.messaging.topics import USER_EVENTS_TOPIC
from messaging.handlers.group_tags_handler import handle_group_tags_update


async def consume_group_tags_events():
    consumer = kafka_manager.create_consumer(
        USER_EVENTS_TOPIC,
        group_id="recipe_service_group_tags_group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            if event.get("event_type") == "update_group_tags":
                handle_group_tags_update(event.get("data"))
    finally:
        await consumer.stop()

