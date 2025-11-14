import os
from dotenv import load_dotenv
from shared.shopping_shared import KafkaConfig, EmailConfig

load_dotenv()

class Config:
    """ General application configuration for Notification-Service. """
    RUN_SETTING = {
        'host': os.getenv('APP_HOST', 'localhost'),
        'port': int(os.getenv('APP_PORT', 1338)), # Different port from user-service
        'debug': os.getenv('DEBUG', 'True').lower() == 'true',
        "access_log": False,
        "auto_reload": True,
    }


class EmailConfig:
    """ Email configuration for Notification-Service. """
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'myemail')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'mypassword')


