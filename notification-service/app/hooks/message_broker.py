# notification-service/app/hooks/message_broker.py
from sanic import Sanic

from app.consumers.notification_consumer import consume_notifications, request_shutdown

from shopping_shared.messaging.kafka_manager import kafka_manager


async def setup_kafka(app: Sanic):
    """Hook to initialize the Kafka connection."""
    kafka_servers = app.config.get("KAFKA_BOOTSTRAP_SERVERS")
    if not kafka_servers:
        # Try to get from the config object if not in app config
        if hasattr(app.config, 'KAFKA') and hasattr(app.config.KAFKA, 'KAFKA_BOOTSTRAP_SERVERS'):
            kafka_servers = app.config.KAFKA.KAFKA_BOOTSTRAP_SERVERS
    kafka_manager.setup(bootstrap_servers=kafka_servers)


async def close_kafka(_app: Sanic):
    """Hook to close the Kafka connection."""
    await kafka_manager.close()


async def start_consumer(app, loop):
    """Start Kafka consumer after server is fully started."""
    app.add_task(consume_notifications(app))


async def stop_consumer(app, loop):
    """Request graceful shutdown of Kafka consumer."""
    request_shutdown()