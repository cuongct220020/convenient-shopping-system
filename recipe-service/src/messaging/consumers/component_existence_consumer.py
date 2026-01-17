from core.messaging import kafka_manager
from shopping_shared.messaging.topics import COMPONENT_EXISTENCE_TOPIC
from messaging.handlers.component_existence_handler import handle_component_existence_update


async def consume_component_existence_events():
    consumer = kafka_manager.create_consumer(
        COMPONENT_EXISTENCE_TOPIC,
        group_id="recipe_service_component_existence_group"
    )
    
    try:
        await consumer.start()
        
        async for msg in consumer:
            try:
                event = msg.value
                event_type = event.get("event_type")
                
                if event_type == "update_component_existence":
                    handle_component_existence_update(event.get("data"))
            except Exception as e:
                pass
    except Exception as e:
        raise
    finally:
        await consumer.stop()

