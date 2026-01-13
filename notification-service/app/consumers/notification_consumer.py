# notification-service/app/consumers/notification_consumer.py
import asyncio
from typing import Dict

from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.messaging.kafka_topics import (
    REGISTRATION_EVENTS_TOPIC,
    RESET_PASSWORD_EVENTS_TOPIC,
    EMAIL_CHANGE_EVENTS_TOPIC,
    LOGOUT_EVENTS_TOPIC,
    NOTIFICATION_TOPIC
)

# Import Handlers
from app.consumers.handlers.base_handler import BaseMessageHandler
from app.consumers.handlers.otp_handler import OTPMessageHandler
from app.consumers.handlers.user_logout_handler import UserLogoutHandler
from app.consumers.handlers.add_user_group_handler import AddUserGroupHandler
from app.consumers.handlers.remove_user_group_handler import RemoveUserGroupHandler
from app.consumers.handlers.user_leave_group_handler import UserLeaveGroupHandler
from app.consumers.handlers.update_head_chef_role_handler import UpdateHeadChefRoleHandler
from app.consumers.handlers.food_expiring_soon_handler import FoodExpiringSoonHandler
from app.consumers.handlers.food_expired_handler import FoodExpiredHandler
from app.consumers.handlers.plan_assigned_handler import PlanAssignedHandler
from app.consumers.handlers.plan_reported_handler import PlanReportedHandler
from app.consumers.handlers.plan_expired_handler import PlanExpiredHandler
from app.consumers.handlers.daily_meal_handler import DailyMealHandler


logger = get_logger("Notification Consumer")

# Global flag for graceful shutdown
_shutdown_event = asyncio.Event()


def request_shutdown():
    """Signal the consumer to shutdown gracefully."""
    _shutdown_event.set()


async def consume_notifications(app=None):
    """
    A long-running task that consumes messages and dispatches them to appropriate handlers.
    
    General Message Format for NOTIFICATION_TOPIC:
    {
        "event_type": str,                    # Required: Event type identifier (e.g., "group_user_added", "food_expiring_soon")
        "group_id": "uuid_string",            # Required: UUID of the group
        "receivers": ["uuid_string"],         # Optional: List of receiver user IDs. If not provided, will be determined by handler logic
        "receiver_is_head_chef": bool,        # Optional: Whether the receiver is the head chef of the group
        "data": {                             # Required: Data fields corresponding to notification_templates
            # Fields vary by template, examples:
            # "group_name": str,
            # "requester_username": str,
            # "unit_name": str,
            # "plan_id": int,
            # etc.
        }
    }
    """
    
    # 1. Define Topic -> Handler Mapping (OTP + system topics)
    topic_handlers: Dict[str, BaseMessageHandler] = {
        REGISTRATION_EVENTS_TOPIC: OTPMessageHandler(expected_action="register"),
        RESET_PASSWORD_EVENTS_TOPIC: OTPMessageHandler(expected_action="reset_password"),
        EMAIL_CHANGE_EVENTS_TOPIC: OTPMessageHandler(expected_action="change_email"),
        LOGOUT_EVENTS_TOPIC: UserLogoutHandler(),
    }
    
    # 2. Define Event Type -> Handler Mapping for NOTIFICATION_TOPIC
    # All non-OTP notifications are routed by event_type
    event_type_handlers: Dict[str, BaseMessageHandler] = {
        "group_user_added": AddUserGroupHandler(),
        "group_user_removed": RemoveUserGroupHandler(),
        "group_user_left": UserLeaveGroupHandler(),
        "group_head_chef_updated": UpdateHeadChefRoleHandler(),
        "food_expiring_soon": FoodExpiringSoonHandler(),
        "food_expired": FoodExpiredHandler(),
        "plan_assigned": PlanAssignedHandler(),
        "plan_reported": PlanReportedHandler(),
        "plan_expired": PlanExpiredHandler(),
        "daily_meal": DailyMealHandler(),
    }
    
    # Combine all topics (topic handlers + NOTIFICATION_TOPIC)
    topics = list(topic_handlers.keys()) + [NOTIFICATION_TOPIC]

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
                if message_topic in topic_handlers:
                    handler = topic_handlers.get(message_topic)
                    if handler:
                        await handler.handle(message_value, app)
                    else:
                        logger.warning(f"No handler found for topic: {message_topic}")
                elif message_topic == NOTIFICATION_TOPIC:
                    # NOTIFICATION_TOPIC: route by event_type
                    event_type = message_value.get("event_type")
                    if not event_type:
                        logger.error(f"Missing event_type in message from {NOTIFICATION_TOPIC}: {message_value}")
                        continue
                    
                    handler = event_type_handlers.get(event_type)
                    if handler:
                        await handler.handle(message_value, app)
                    else:
                        logger.warning(f"No handler found for event_type: {event_type}")
                else:
                    logger.warning(f"Unknown topic: {message_topic}")

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
