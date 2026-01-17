from core.messaging import kafka_manager
from shopping_shared.messaging.kafka_topics import USER_UPDATE_TAG_EVENTS_TOPIC
from messaging.handlers.group_tags_handler import handle_group_tags_update


async def consume_group_tags_events():
    consumer = kafka_manager.create_consumer(
        USER_UPDATE_TAG_EVENTS_TOPIC,
        group_id="recipe_service_group_tags_group"
    )
    
    try:
        await consumer.start()
        
        async for msg in consumer:
            try:
                event = msg.value
                event_type = event.get("event_type")
                
                if event_type == "user_tags_updated":
                    handle_group_tags_update(event)
            except Exception as e:
                pass
    except Exception as e:
        raise
    finally:
        await consumer.stop()

