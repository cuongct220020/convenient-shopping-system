# user-service/app/services/kafka_service.py
from datetime import datetime, UTC

from app.enums import OtpAction
from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.messaging.kafka_topics import (
    REGISTRATION_EVENTS_TOPIC,
    RESET_PASSWORD_EVENTS_TOPIC,
    EMAIL_CHANGE_EVENTS_TOPIC,
    USER_UPDATE_TAG_EVENTS_TOPIC,
    LOGOUT_EVENTS_TOPIC,
    NOTIFICATION_TOPIC,
)


logger = get_logger("Kafka Service")

class KafkaService:

    @staticmethod
    async def publish_otp_message(email: str, otp_code: str, action: str) -> None:
        """
        Publish user registration otp via Kafka.
        """
        if action == OtpAction.REGISTER.value:
            topic = REGISTRATION_EVENTS_TOPIC
        elif action == OtpAction.RESET_PASSWORD.value:
            topic = RESET_PASSWORD_EVENTS_TOPIC
        elif action == OtpAction.CHANGE_EMAIL.value:
            topic = EMAIL_CHANGE_EVENTS_TOPIC
        else:
            logger.error(f"Invalid action for publishing OTP: {action}")
            raise ValueError("Invalid action for publishing OTP.")


        payload = {
            "email": email,
            "otp_code": otp_code,
            "action": action
        }

        try:
            # Use safe send_message with idempotence and wait=True
            await kafka_manager.send_message(
                topic=topic, 
                value=payload, 
                key=email, # Ensure ordering by email
                wait=True
            )
            logger.info("User registration otp published.")

        except Exception as e:
            logger.error(f"Failed to publish user registration otp: {e}")
            raise e

    @staticmethod
    def _build_payload(**kwargs) -> dict:
        """Private helper to build payload dictionary with timestamp."""
        from uuid import UUID

        def convert_uuids(obj):
            """Convert UUID objects to strings recursively."""
            if isinstance(obj, UUID):
                return str(obj)
            elif isinstance(obj, dict):
                return {key: convert_uuids(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_uuids(item) for item in obj]
            elif isinstance(obj, tuple):
                return tuple(convert_uuids(item) for item in obj)
            else:
                return obj

        timestamp = datetime.now(UTC)
        payload = {"timestamp": timestamp}
        payload.update(kwargs)

        return convert_uuids(payload)

    @staticmethod
    async def _publish_message(topic: str, payload: dict, key: str):
        """Private helper to publish message to Kafka."""
        try:
            await kafka_manager.send_message(
                topic=topic,
                value=payload,
                key=key,
                wait=True
            )
        except Exception as e:
            logger.error(f"Failed to publish message to topic {topic}: {e}")
            raise e

    @staticmethod
    async def publish_add_user_group_message(
        requester_username: str,
        group_id: str,
        user_to_add_id: str,
        topic: str = NOTIFICATION_TOPIC
    ):
        payload = {
            "event_type": "group_user_added",
            "group_id": str(group_id),
            "receivers": [str(user_to_add_id)],
            "data": {
                "requester_username": str(requester_username),
            },
        }

        await kafka_service._publish_message(
            topic=topic,
            payload=payload,
            key=f"{group_id}-group"
        )

        logger.info(f"Group user added message published successfully to topic: {topic}")


    @staticmethod
    async def publish_remove_user_group_message(
        requester_username: str,
        user_to_remove_id: str,
        group_id: str,
    ):
        payload = {
            "event_type": "group_user_removed",
            "group_id": str(group_id),
            "receivers": [str(user_to_remove_id)],
            "data": {
                "requester_username": str(requester_username),
            },
        }

        try:
            await kafka_service._publish_message(
                topic=NOTIFICATION_TOPIC,
                payload=payload,
                key=f"{group_id}-group"
            )
        except Exception as err:
            logger.error(f"Failed to publish remove user group message: {err}")
            raise err


    @staticmethod
    async def publish_user_leave_group_message(
        user_id: str,
        group_id: str,
        topic: str = NOTIFICATION_TOPIC
    ):
        payload = {
            "event_type": "group_user_left",
            "group_id": str(group_id),
            "receivers": [str(user_id)],
            "data": {},
        }

        await kafka_service._publish_message(
            topic=topic,
            payload=payload,
            key=f"{group_id}-group"
        )

        logger.info(f"User leave group message published successfully to topic: {topic}")


    @staticmethod
    async def  publish_user_logout_message(
        user_id: str,
        jti: str,
        topic: str = LOGOUT_EVENTS_TOPIC
    ):
        payload = kafka_service._build_payload(
            event_type="account_logged_out",
            user_id=str(user_id),
            access_token_id=str(jti),
            timestamp=str(datetime.now(UTC)),
        )

        await kafka_service._publish_message(
            topic=topic,
            payload=payload,
            key=str(user_id)
        )

    @staticmethod
    async def publish_update_headchef_group_message(
        requester_username: str,
        group_id: str,
        new_head_chef_username: str,
    ):
        payload = {
            "event_type": "group_head_chef_updated",
            "group_id": str(group_id),
            "receivers": [],
            "data": {
                "new_head_chef_username": str(new_head_chef_username),
                "requester_username": str(requester_username),
            },
        }

        try:
            await kafka_service._publish_message(
                topic=NOTIFICATION_TOPIC,
                payload=payload,
                key=f"{group_id}-group"
            )

        except Exception as e:
            logger.error(f"Failed to publish update head chef role message: {e}")
            raise e


    @staticmethod
    async def publish_user_update_tag_message(
        topic: str = USER_UPDATE_TAG_EVENTS_TOPIC
    ):
        pass


kafka_service = KafkaService()