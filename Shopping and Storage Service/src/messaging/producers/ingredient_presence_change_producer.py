from messaging.manager import kafka_manager

async def produce_ingredient_presence_change(group_id: int, component_name: str, is_present: bool):
    producer = await kafka_manager.get_producer()
    event = {
        "event_type": "ingredient_present" if is_present else "ingredient_absent",
        "data": {
            "group_id": group_id,
            "component_name": component_name
        }
    }
    await producer.send_and_wait(
        topic="ingredient_presence_change",
        value=event,
        timeout=10
    )