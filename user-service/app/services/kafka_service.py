# user-service/app/services/kafka_service.py
from pydantic import EmailStr

from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger

USER_REGISTRATION_OTP_TOPIC = "user_registration_otp"

logger = get_logger("Kafka Service")

class KafkaService:

    @staticmethod
    async def publish_user_registration_otp(email: EmailStr, otp_code: str) -> None:
        """
        Publish user registration otp via Kafka.
        """

        topic = USER_REGISTRATION_OTP_TOPIC
        payload = {
            "email": email,
            "otp_code": otp_code,
            "action": "register"
        }

        try:
            producer = await kafka_manager.get_producer()
            await producer.send_and_wait(topic, value=payload)
            logger.info("User registration otp published.")

        except Exception as e:
            logger.error(f"Failed to publish user registration otp: {e}")
            raise e

kafka_service = KafkaService()