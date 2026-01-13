from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.messaging.topics import COMPONENT_EXISTENCE_TOPIC
from messaging.handlers.component_existence_handler import handle_component_existence_update
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("ComponentExistenceConsumer")


async def consume_component_existence_events():
    consumer = kafka_manager.create_consumer(
        COMPONENT_EXISTENCE_TOPIC,
        group_id="recipe_service_component_existence_group"
    )
    
    try:
        await consumer.start()
        logger.info("Component existence consumer started")
        
        async for msg in consumer:
            try:
                event = msg.value
                event_type = event.get("event_type")
                if event_type == "update_component_existence":
                    handle_component_existence_update(event.get("data"))
                else:
                    logger.warning(f"Unknown event_type: {event_type}, partition={msg.partition}, offset={msg.offset}")
            except Exception as e:
                logger.error(f"Error processing message: partition={msg.partition}, offset={msg.offset}, error={str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Error in component existence consumer: {str(e)}", exc_info=True)
        raise
    finally:
        await consumer.stop()
        logger.info("Component existence consumer stopped")

