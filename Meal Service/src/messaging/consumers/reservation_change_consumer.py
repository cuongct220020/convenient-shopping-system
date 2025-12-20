from messaging.manager import kafka_manager
from messaging.handlers.reservation_change_handler import handle_unit_shortage, handle_unit_allocated

async def sufficiency_updated_consumer():
    consumer = kafka_manager.create_consumer(
        "reservation_change",
        group_id="meal_service_reservation_change_consumer"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            if event.get("event_type") == "unit_allocated":
                handle_unit_allocated(event["data"])
            elif event.get("event_type") == "unit_shortage":
                handle_unit_shortage(event["data"])
    finally:
        await consumer.stop()

