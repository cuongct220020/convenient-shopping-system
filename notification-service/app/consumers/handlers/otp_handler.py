# notification-service/app/consumers/handlers/otp_handler.py
from shopping_shared.utils.logger_utils import get_logger
from .base_handler import BaseMessageHandler

logger = get_logger("OTP Handler")

class OTPMessageHandler(BaseMessageHandler):
    """
    Generic Handler for OTP related events.
    Can be reused for Register, Reset Password, Change Email since logic is identical.
    """
    
    def __init__(self, expected_action: str = None):
        """
        :param expected_action: Optional validation to ensure handler only processes specific actions.
        """
        self.expected_action = expected_action

    async def handle(self, message_value: dict, app):
        email = message_value.get("email")
        otp_code = message_value.get("otp_code")
        action = message_value.get("action")

        # Validate message structure
        if not email or not otp_code:
            logger.warning(f"Invalid message format: {message_value}")
            return

        # Validate action matches handler responsibility (if specified)
        if self.expected_action and action != self.expected_action:
             logger.warning(f"Action mismatch: Expected {self.expected_action}, got {action}. Skipping.")
             return

        logger.info(f"Processing OTP action '{action}' for email {email}")
        
        if app and hasattr(app.ctx, 'email_service'):
            try:
                await app.ctx.email_service.send_otp(
                    email=email,
                    otp_code=otp_code,
                    action=action
                )
                logger.info(f"OTP email sent successfully to {email}")
            except Exception as e:
                logger.error(f"Failed to send OTP email: {e}")
                raise e # Re-raise to trigger consumer error handling (retry or log)
        else:
            logger.error("Email service not available in app context")
            raise RuntimeError("Email service dependency missing")
