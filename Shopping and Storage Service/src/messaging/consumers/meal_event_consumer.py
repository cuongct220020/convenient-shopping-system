from messaging.manager import kafka_manager

async def meal_event_consumer():
    consumer = kafka_manager.create_consumer(
        "meal_event",
        group_id="shopping_storage_service_meal_event_consumer"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            if event.get("event_type") == "meal_upserted":
                handle_meal_upserted(event["data"])
            elif event.get("event_type") == "meal_deleted":
                handle_meal_deleted(event["data"])
    finally:
        await consumer.stop()