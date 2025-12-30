# user-service/app/services/kafka_service.py
from app.enums import OtpAction
from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.messaging.kafka_topics import (
    REGISTRATION_EVENTS_TOPIC,
    RESET_PASSWORD_EVENTS_TOPIC,
    EMAIL_CHANGE_EVENTS_TOPIC,
    ADD_USERS_GROUP_EVENTS_TOPIC,
    USER_UPDATE_TAG_EVENTS_TOPIC
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
    async def publish_group_user_added_message(
        requester_id: str,
        group_id: str,
        user_to_add_id: str,
        user_to_add_identifier: str,
        topic: str = ADD_USERS_GROUP_EVENTS_TOPIC
    ):
        payload = {
            "requester_id": str(requester_id),  # Convert UUID to string
            "group_id": str(group_id),          # Convert UUID to string
            "user_to_add_id": str(user_to_add_id),  # Convert UUID to string
            "user_to_add_identifier": user_to_add_identifier
        }


        try:
            await kafka_manager.send_message(
                topic=topic,
                value=payload,
                key=str(group_id),  # Convert UUID to string
                wait=True
            )
            logger.info(f"Group user added message published successfully to topic: {topic}")
        except Exception as e:
            logger.error(f"Failed to publish group user added message to topic {topic}: {e}")
            raise e


    @staticmethod
    async def publish_user_update_tag_message(
        topic: str = USER_UPDATE_TAG_EVENTS_TOPIC
    ):
        pass


kafka_service = KafkaService()