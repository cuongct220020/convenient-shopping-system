# user-service/app/services/kafka_service.py
from app.enums import OtpAction
from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.messaging.kafka_topics import (
    REGISTRATION_EVENTS_TOPIC,
    RESET_PASSWORD_EVENTS_TOPIC,
    EMAIL_CHANGE_EVENTS_TOPIC
)


logger = get_logger("Kafka Service")

class KafkaService:

    @staticmethod
    async def publish_message(email: str, otp_code: str, action: str) -> None:
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

kafka_service = KafkaService()