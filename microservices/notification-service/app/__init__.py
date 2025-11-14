from sanic import Sanic
from shared.shopping_shared.utils.logger_utils import get_logger
from shared.shopping_shared import kafka_manager
from app.services.email_service import email_service
from app.consumers.notification_consumer import consume_notifications

logger = get_logger(__name__)

def setup_listeners(app: Sanic):
    """Initializes services and sets up background tasks."""
    
    @app.listener("before_server_start")
    async def initialize_services(app, loop):
        # Initialize Kafka Manager
        kafka_servers = app.config.get("KAFKA_BOOTSTRAP_SERVERS")
        kafka_manager.setup(bootstrap_servers=kafka_servers)
        logger.info("Kafka manager initialized.")

        # Initialize Email Service
        email_service.init_app(app)
        logger.info("Email service initialized.")

        # Start the Kafka consumer as a background task
        app.add_task(consume_notifications())

    @app.listener("after_server_stop")
    async def cleanup(app, loop):
        await kafka_manager.close()
        logger.info("Kafka manager closed.")


def create_app(*config_cls) -> Sanic:
    """Application factory for the Notification Service."""
    logger.info("Notification service application starting...")
    
    app = Sanic("NotificationService")

    # Load configurations
    for config in config_cls:
        app.update_config(config)

    # Register listeners and background tasks
    setup_listeners(app)

    @app.get("/health")
    async def health_check(request):
        return {"status": "ok"}

    return app
