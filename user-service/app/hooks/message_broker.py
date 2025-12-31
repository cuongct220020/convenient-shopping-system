# user-service/app/hooks/message_broker.py
import asyncio
from sanic import Sanic
from shopping_shared.messaging.kafka_manager import kafka_manager
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Message Broker Hooks")


async def setup_kafka(app: Sanic):
    """Hook to initialize the Kafka connection."""
    logger.info("Initializing Kafka producer...")
    kafka_servers = app.config.KAFKA.KAFKA_BOOTSTRAP_SERVERS
    kafka_manager.setup(bootstrap_servers=kafka_servers)
    # # Initialize the producer on startup
    # await kafka_manager.get_producer()


async def close_kafka(_app: Sanic):
    """Hook to close the Kafka connection."""
    logger.info("Closing Kafka manager...")
    try:
        # Close the Kafka manager with timeout
        await asyncio.wait_for(kafka_manager.close(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.warning("Kafka manager close operation timed out, forcing shutdown")
        # Force close without waiting
        try:
            kafka_manager.close()
        except:
            pass  # Ignore errors during force close
    except Exception as e:
        logger.error(f"Error during Kafka manager shutdown: {e}")
    logger.info("Kafka manager closed.")
