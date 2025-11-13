import os
from dotenv import load_dotenv
from shopping_shared.configs import KafkaConfig, EmailConfig

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

