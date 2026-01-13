from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.messaging.kafka_topics import USER_UPDATE_TAG_EVENTS_TOPIC
from messaging.handlers.group_tags_handler import handle_group_tags_update
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("GroupTagsConsumer")


async def consume_group_tags_events():
    consumer = kafka_manager.create_consumer(
        USER_UPDATE_TAG_EVENTS_TOPIC,
        group_id="recipe_service_group_tags_group"
    )
    
    try:
        await consumer.start()
        logger.info("Group tags consumer started")
        
        async for msg in consumer:
            try:
                event = msg.value
                event_type = event.get("event_type")
                if event_type == "user_tags_updated":
                    handle_group_tags_update(event)
                else:
                    logger.warning(f"Unknown event_type: {event_type}, partition={msg.partition}, offset={msg.offset}")
            except Exception as e:
                logger.error(f"Error processing message: partition={msg.partition}, offset={msg.offset}, error={str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Error in group tags consumer: {str(e)}", exc_info=True)
        raise
    finally:
        await consumer.stop()
        logger.info("Group tags consumer stopped")

