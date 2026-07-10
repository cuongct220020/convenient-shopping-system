# app/services/email_service.py
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from shopping_shared.utils.logger_utils import get_logger

from jinja2 import Environment, PackageLoader, select_autoescape

logger = get_logger("Email Service")

class EmailService:
    def __init__(self, config=None):
        self.config = config
        self.jinja_env = Environment(
            loader=PackageLoader("app", "templates"),
            autoescape=select_autoescape()
        )
        if config:
            logger.info("EmailService initialized (Async).")

    async def _send_email(self, to_email: str, subject: str, html_content: str):
        if not self.config:
            logger.error("Email service not initialized.")
            return

        # Access config safely (Sanic config behaves like a dict or object depending on version)
        sender_email = getattr(self.config, 'EMAIL_SENDER', None) or self.config.get('EMAIL_SENDER')
        password = getattr(self.config, 'EMAIL_PASSWORD', None) or self.config.get('EMAIL_PASSWORD')
        host = getattr(self.config, 'EMAIL_HOST', None) or self.config.get('EMAIL_HOST')
        port = getattr(self.config, 'EMAIL_PORT', None) or self.config.get('EMAIL_PORT')
        use_tls = getattr(self.config, 'EMAIL_USE_TLS', None) or self.config.get('EMAIL_USE_TLS', True)

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = to_email
        message.attach(MIMEText(html_content, "html"))

        try:
            # Sử dụng aiosmtplib để gửi mail bất đồng bộ
            # Mailpit (port 1025) không yêu cầu xác thực
            # Gmail thường dùng start_tls=True ở port 587
            if port == 1025:  # Mailpit port - không cần xác thực
                await aiosmtplib.send(
                    message,
                    hostname=host,
                    port=port
                    # Không cần username và password cho Mailpit
                )
            elif port == 587:
                await aiosmtplib.send(
                    message,
                    hostname=host,
                    port=port,
                    username=sender_email,
                    password=password,
                    start_tls=True  # For port 587
                )
            else:
                await aiosmtplib.send(
                    message,
                    hostname=host,
                    port=port,
                    username=sender_email,
                    password=password,
                    use_tls=use_tls  # For other ports like 465
                )
            logger.info(f"Successfully sent email to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}. Error: {e}")

    async def send_otp(self, email: str, otp_code: str, action: str):
        """
        Constructs and sends an OTP email based on the action.
        """
        # Map action to template and subject
        action_config = {
            "register": {
                "template": "register_otp.html",
                "subject": "Welcome! Your Verification Code"
            },
            "reset_password": {
                "template": "reset_password_otp.html",
                "subject": "Your Password Reset Code"
            },
            "change_email": {
                "template": "change_email_otp.html",
                "subject": "Your Email Change Verification Code"
            }
        }

        if action not in action_config:
            logger.warning(f"Attempted to send OTP for unknown action: {action}")
            return

        config = action_config[action]
        template = self.jinja_env.get_template(config["template"])
        body_html = template.render(otp_code=otp_code)

        await self._send_email(to_email=email, subject=config["subject"], html_content=body_html)
