from shared.shopping_shared.messaging.kafka_manager import kafka_manager
from shared.shopping_shared.messaging.topics import COMPONENT_EXISTENCE_TOPIC
from messaging.handlers.component_existence_handler import handle_component_existence_update


async def consume_component_existence_events():
    consumer = kafka_manager.create_consumer(
        COMPONENT_EXISTENCE_TOPIC,
        group_id="recipe_service_component_existence_group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            if event.get("event_type") == "update_component_existence":
                await handle_component_existence_update(event.get("data"))
    finally:
        await consumer.stop()

