from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger
from app.services.email_service import email_service

logger = get_logger("Notification Consumer")

async def consume_notifications():
    """
    A long-running task that consumes messages from the 'user_registration_otp' topic
    and processes them.
    """
    # Topic must match what user-service is producing to
    topic = "user_registration_otp"
    
    consumer = kafka_manager.create_consumer(
        topic,
        group_id="notification_service_group" 
    )
    await consumer.start()
    logger.info(f"Notification consumer started and listening on '{topic}'...")
    try:
        async for msg in consumer:
            logger.info(f"Received message: {msg.value}")
            try:
                # User service sends a flat JSON structure: {"email": "...", "otp_code": "...", "action": "..."}
                message_data = msg.value
                
                email = message_data.get("email")
                otp_code = message_data.get("otp_code")
                action = message_data.get("action")

                if email and otp_code:
                    logger.info(f"Processing OTP email for {email} (Action: {action})")
                    await email_service.send_otp(
                        email=email,
                        otp_code=otp_code,
                        action=action
                    )
                else:
                    logger.warning(f"Received invalid message format: {message_data}")

            except Exception as e:
                logger.error(f"Failed to process message: {msg.value}. Error: {e}", exc_info=True)
    finally:
        logger.info("Stopping notification consumer...")
        await consumer.stop()
