from messaging.manager import kafka_manager
from messaging.handlers.sufficiency_updated_handler import sufficiency_updated_handler

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
                await sufficiency_updated_handler(event["data"])
    finally:
        await consumer.stop()

