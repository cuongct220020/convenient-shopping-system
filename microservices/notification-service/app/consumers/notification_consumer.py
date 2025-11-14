from shared.shopping_shared import kafka_manager
from shared.shopping_shared.messaging.topics import NOTIFICATION_TOPIC
from shared.shopping_shared.utils.logger_utils import get_logger
from app.services.email_service import email_service

logger = get_logger(__name__)

async def consume_notifications():
    """
    A long-running task that consumes messages from the NOTIFICATION_TOPIC
    and processes them.
    """
    consumer = kafka_manager.create_consumer(
        NOTIFICATION_TOPIC,
        group_id="notification_service_group" # A unique groups ID for this service
    )
    await consumer.start()
    logger.info("Notification consumer started and listening for messages...")
    try:
        async for msg in consumer:
            logger.info(f"Received message: {msg.value}")
            try:
                message_data = msg.value
                message_type = message_data.get("type")
                payload = message_data.get("payload")

                if message_type == "send_otp" and payload:
                    await email_service.send_otp(
                        email=payload.get("email"),
                        otp_code=payload.get("otp_code"),
                        action=payload.get("action")
                    )
                else:
                    logger.warning(f"Received unknown message type: {message_type}")

            except Exception as e:
                logger.error(f"Failed to process message: {msg.value}. Error: {e}", exc_info=True)
    finally:
        logger.info("Stopping notification consumer...")
        await consumer.stop()
