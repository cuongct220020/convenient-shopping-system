# notification-service/app/consumers/handlers/otp_handler.py
from .base_handler import BaseMessageHandler

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
            return

        # Validate action matches handler responsibility (if specified)
        if self.expected_action and action != self.expected_action:
             return

        if app and hasattr(app.ctx, 'email_service'):
            try:
                await app.ctx.email_service.send_otp(
                    email=email,
                    otp_code=otp_code,
                    action=action
                )
            except Exception as e:
                raise e # Re-raise to trigger consumer error handling (retry or log)
        else:
            raise RuntimeError("Email service dependency missing")
