# notification-service/app/consumers/notification_consumer.py
import asyncio
from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger
from app.services.email_service import email_service

logger = get_logger("Notification Consumer")

# Global flag for graceful shutdown
_shutdown_event = asyncio.Event()


def request_shutdown():
    """Signal the consumer to shutdown gracefully."""
    _shutdown_event.set()


async def consume_notifications():
    """
    A long-running task that consumes messages from the 'user_registration_otp' topic
    and processes them.
    """
    # Topic must match what user-service is producing to
    topic = "user_registration_otp"

    max_retries = 10
    retry_count = 0
    consumer = None

    # Check if kafka_manager is properly initialized
    if kafka_manager is None or kafka_manager.bootstrap_servers is None:
        logger.warning("Kafka is not configured. Consumer will not start.")
        logger.info("To enable Kafka, set KAFKA_BOOTSTRAP_SERVERS environment variable.")
        return

    while retry_count < max_retries and not _shutdown_event.is_set():
        try:
            consumer = kafka_manager.create_consumer(
                topic,
                group_id="notification_service_group",
                # Add some consumer-specific configurations to handle connection issues
                request_timeout_ms=30000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
            )
            await consumer.start()
            logger.info(f"Notification consumer started and listening on '{topic}'...")
            break
        except asyncio.CancelledError:
            logger.info("Consumer startup was cancelled.")
            return
        except Exception as e:
            retry_count += 1
            logger.warning(f"Failed to start consumer (attempt {retry_count}/{max_retries}): {e}")
            if retry_count >= max_retries:
                logger.warning(
                    "Max retries reached. Consumer will not run. "
                    "Please ensure Kafka is running and accessible."
                )
                return
            # Wait before retrying, but check for shutdown
            try:
                await asyncio.wait_for(_shutdown_event.wait(), timeout=5.0)
                logger.info("Shutdown requested during retry wait.")
                return
            except asyncio.TimeoutError:
                pass  # Continue to retry

    if consumer is None:
        return

    try:
        async for msg in consumer:
            if _shutdown_event.is_set():
                break

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
    except asyncio.CancelledError:
        logger.info("Consumer was cancelled.")
    except Exception as e:
        logger.error(f"Consumer error: {e}", exc_info=True)
    finally:
        logger.info("Stopping notification consumer...")
        if consumer is not None:
            try:
                await consumer.stop()
                logger.info("Consumer stopped successfully.")
            except Exception as e:
                logger.error(f"Error stopping consumer: {e}")
