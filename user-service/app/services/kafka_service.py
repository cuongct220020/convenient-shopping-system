# user-service/app/services/kafka_service.py
from app.enums import OtpAction
from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.messaging.kafka_topics import (
    REGISTRATION_EVENTS_TOPIC,
    PASSWORD_RESET_EVENTS_TOPIC,
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
            topic = PASSWORD_RESET_EVENTS_TOPIC
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
            producer = await kafka_manager.get_producer()
            await producer.send_and_wait(topic, value=payload)
            logger.info("User registration otp published.")

        except Exception as e:
            logger.error(f"Failed to publish user registration otp: {e}")
            raise e

kafka_service = KafkaService()