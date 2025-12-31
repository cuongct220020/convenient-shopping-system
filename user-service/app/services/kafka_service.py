# user-service/app/services/kafka_service.py
from datetime import datetime, UTC
from typing import List

from app.enums import OtpAction, GroupRole
from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.messaging.kafka_topics import (
    REGISTRATION_EVENTS_TOPIC,
    RESET_PASSWORD_EVENTS_TOPIC,
    EMAIL_CHANGE_EVENTS_TOPIC,
    ADD_USERS_GROUP_EVENTS_TOPIC,
    USER_UPDATE_TAG_EVENTS_TOPIC,
    LOGOUT_EVENTS_TOPIC,
    LEAVE_GROUP_EVENTS_TOPIC,
    REMOVE_USERS_GROUP_EVENTS_TOPIC,
    UPDATE_HEADCHEF_ROLE_EVENTS_TOPIC
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
        requester_id: str,
        group_id: str,
        user_to_add_id: str,
        user_to_add_identifier: str,
        group_members_ids: List[str],
        topic: str = ADD_USERS_GROUP_EVENTS_TOPIC
    ):
        payload = kafka_service._build_payload(
            event_type="ADD_USER_GROUP",
            requester_id=str(requester_id),
            group_id=str(group_id),
            user_to_add_id=str(user_to_add_id),
            user_to_add_identifier=user_to_add_identifier,
            group_members_ids=group_members_ids
        )

        await kafka_service._publish_message(
            topic=topic,
            payload=payload,
            key=str(group_id)
        )
        logger.info(f"Group user added message published successfully to topic: {topic}")


    async def publish_remove_user_group_message(
        self,
        requester_id: str,
        target_user_id: str,
        group_id: str
    ):
        payload = self._build_payload(
            event_type="REMOVE_USER_GROUP",
            requester_id=str(requester_id),
            target_user_id=str(target_user_id),
            group_id=str(group_id)
        )

        try:
            await kafka_service._publish_message(
                topic=REMOVE_USERS_GROUP_EVENTS_TOPIC,
                payload=payload,
                key=str(group_id)
            )
        except Exception as err:
            logger.error(f"Failed to publish remove user group message: {err}")
            raise err


    @staticmethod
    async def publish_user_leave_group_message(
        user_id: str,
        group_id: str,
        topic: str = LEAVE_GROUP_EVENTS_TOPIC
    ):
        payload = kafka_service._build_payload(
            event_type="USER_LEAVE_GROUP",
            user_id=str(user_id),
            group_id=str(group_id)
        )

        await kafka_service._publish_message(
            topic=topic,
            payload=payload,
            key=str(group_id)
        )
        logger.info(f"User leave group message published successfully to topic: {topic}")


    @staticmethod
    async def publish_user_logout_message(
        user_id: str,
        jti: str,
        topic: str = LOGOUT_EVENTS_TOPIC
    ):
        payload = kafka_service._build_payload(
            event_type="USER_LOGOUT",
            user_id=str(user_id),
            access_token_id=str(jti)
        )

        await kafka_service._publish_message(
            topic=topic,
            payload=payload,
            key=str(user_id)
        )

    @staticmethod
    async def publish_update_headchef_group_message(
        requester_id: str,
        group_id: str,
        target_user_id: str,
        target_user_role: GroupRole = GroupRole.HEAD_CHEF
    ):
        payload = kafka_service._build_payload(
            event_type="NEW_HEAD_CHEF_GROUP",
            requester_id=str(requester_id),
            group_id=str(group_id),
            target_user_id=str(target_user_id),
            target_user_role=str(target_user_role)
        )

        try:
            await kafka_service._publish_message(
                topic = UPDATE_HEADCHEF_ROLE_EVENTS_TOPIC,
                payload=payload,
                key=str(group_id)
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