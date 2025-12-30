# notification-service/app/consumers/notification_consumer.py
import asyncio
from typing import Dict

from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.messaging.kafka_topics import (
    REGISTRATION_EVENTS_TOPIC,
    RESET_PASSWORD_EVENTS_TOPIC,
    EMAIL_CHANGE_EVENTS_TOPIC,
    ADD_USERS_GROUP_EVENTS_TOPIC
)

# Import Handlers
from app.consumers.handlers.base_handler import BaseMessageHandler
from app.consumers.handlers.otp_handler import OTPMessageHandler
from app.consumers.handlers.family_group_handler import AddUserGroupHandler


logger = get_logger("Notification Consumer")

# Global flag for graceful shutdown
_shutdown_event = asyncio.Event()


def request_shutdown():
    """Signal the consumer to shutdown gracefully."""
    _shutdown_event.set()


async def consume_notifications(app=None):
    """
    A long-running task that consumes messages and dispatches them to appropriate handlers.
    """
    
    # 1. Define Topic -> Handler Mapping
    # We use the same generic OTPMessageHandler but configured for specific actions validation
    handlers: Dict[str, BaseMessageHandler] = {
        REGISTRATION_EVENTS_TOPIC: OTPMessageHandler(expected_action="register"),
        RESET_PASSWORD_EVENTS_TOPIC: OTPMessageHandler(expected_action="reset_password"),
        EMAIL_CHANGE_EVENTS_TOPIC: OTPMessageHandler(expected_action="change_email"),
        ADD_USERS_GROUP_EVENTS_TOPIC: AddUserGroupHandler()
    }
    
    topics = list(handlers.keys())

    max_retries = 10
    retry_count = 0
    consumer = None

    if kafka_manager is None or kafka_manager.bootstrap_servers is None:
        logger.warning("Kafka is not configured. Consumer will not start.")
        return

    # 2. Connect to Kafka
    while retry_count < max_retries and not _shutdown_event.is_set():
        try:
            consumer = kafka_manager.create_consumer(
                *topics,
                group_id="notification_service_group",
                request_timeout_ms=30000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
                enable_auto_commit=False # Explicitly disable auto-commit
            )
            await consumer.start()
            logger.info(f"Notification consumer started. Listening on: {topics}")
            break
        except asyncio.CancelledError:
            logger.info("Consumer startup was cancelled.")
            return
        except Exception as e:
            retry_count += 1
            logger.warning(f"Failed to start consumer (attempt {retry_count}/{max_retries}): {e}")
            if retry_count >= max_retries:
                logger.error("Max retries reached. Consumer failed to start.")
                return
            try:
                await asyncio.wait_for(_shutdown_event.wait(), timeout=5.0)
                return
            except asyncio.TimeoutError:
                pass

    if consumer is None:
        return

    # 3. Main Loop
    try:
        async for msg in consumer:
            if _shutdown_event.is_set():
                break

            try:
                message_topic = msg.topic
                message_value = msg.value # Already deserialized by KafkaManager (orjson/json)
                
                logger.debug(f"Received message on {message_topic}: {message_value}")

                # Dispatch to Handler
                handler = handlers.get(message_topic)
                if handler:
                    await handler.handle(message_value, app)
                else:
                    logger.warning(f"No handler found for topic: {message_topic}")

            except Exception as e:
                # Log error but don't crash the loop.
                # In production, consider DLQ (Dead Letter Queue) logic here.
                logger.error(f"Error processing message from {msg.topic}: {e}", exc_info=True)
            
            # 4. Manual Commit (At-Least-Once delivery)
            # We commit even on error to avoid infinite loops (poison pill). 
            # Ideally, failed messages should go to a DLQ before commit.
            try:
                await consumer.commit()
            except Exception as commit_error:
                logger.error(f"Failed to commit offset: {commit_error}")

    except asyncio.CancelledError:
        logger.info("Consumer task cancelled.")
    except Exception as e:
        logger.critical(f"Critical consumer error: {e}", exc_info=True)
    finally:
        logger.info("Stopping notification consumer...")
        if consumer:
            await consumer.stop()
            logger.info("Consumer stopped.")
