import os
from dotenv import load_dotenv
from shopping_shared.configs import KafkaConfig

# Load environment variables
load_dotenv()

class Config:
    """ General application configuration for Notification-Service. """

    RUN_SETTING = {
        'host': os.getenv('APP_HOST', 'localhost'),
        'port': int(os.getenv('APP_PORT', '8000')),
        'debug': os.getenv('DEBUG', True).lower() == 'true',
        "access_log": False,
        "auto_reload": True,
        'workers': int(os.getenv('WORKERS', 1)),
    }

    KAFKA = KafkaConfig(
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    )

    # Email Configuration
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
    EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'noreply@convenient-shopping-system.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'mypassword')


