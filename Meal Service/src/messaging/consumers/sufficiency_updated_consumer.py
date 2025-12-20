from messaging.manager import kafka_manager
from messaging.handlers.sufficiency_updated_handler import handle_sufficiency_update

async def sufficiency_updated_consumer():
    consumer = kafka_manager.create_consumer(
        "unit_updated",
        group_id="meal_service_unit_updated_listener"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            if event.get("event_type") == "meal_sufficiency_updated":
                handle_sufficiency_update(event["data"])
    finally:
        await consumer.stop()

