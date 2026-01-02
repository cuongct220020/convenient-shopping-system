# notification-service/app/hooks/message_broker.py
from sanic import Sanic
from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Message Broker Hooks")


async def setup_kafka(app: Sanic):
    """Hook to initialize the Kafka connection."""
    logger.info("Initializing Kafka consumer...")
    kafka_servers = app.config.get("KAFKA_BOOTSTRAP_SERVERS")
    if not kafka_servers:
        # Try to get from the config object if not in app config
        if hasattr(app.config, 'KAFKA') and hasattr(app.config.KAFKA, 'KAFKA_BOOTSTRAP_SERVERS'):
            kafka_servers = app.config.KAFKA.KAFKA_BOOTSTRAP_SERVERS
    kafka_manager.setup(bootstrap_servers=kafka_servers)
    logger.info(f"Kafka manager initialized with servers: {kafka_servers}")


async def close_kafka(_app: Sanic):
    """Hook to close the Kafka connection."""
    logger.info("Closing Kafka manager...")
    await kafka_manager.close()
    logger.info("Kafka manager closed.")
