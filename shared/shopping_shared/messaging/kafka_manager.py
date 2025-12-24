# shared/shopping_shared/messaging/kafka_manager.py

import json
from typing import Optional

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError as AIOKafkaError

from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.exceptions import MessageBrokerError, KafkaConnectionError

logger = get_logger("Kafka Manager")


class KafkaManager:
    """
    Manages Kafka producer and consumer connections for the application.
    Provides a centralized point for creating and managing Kafka clients.
    """

    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None
        self._bootstrap_servers: str = ""

    def setup(self, bootstrap_servers: str):
        """
        Stores the Kafka bootstrap servers configuration.
        """
        if not bootstrap_servers:
            raise ValueError("Kafka bootstrap servers must be provided.")
        self._bootstrap_servers = bootstrap_servers
        logger.info(f"KafkaManager setup with bootstrap servers: {bootstrap_servers}")

    async def get_producer(self) -> AIOKafkaProducer:
        """
        Initializes and returns a singleton AIOKafkaProducer instance.
        The producer is started on its first retrieval.

        Performance optimizations:
        - linger_ms: Batch messages for 5ms before sending (reduces network calls)
        - batch_size: Max bytes per batch (default 16KB, increased to 32KB)
        - compression_type: gzip compression reduces network bandwidth
        - acks='all': Ensures durability (can use acks=1 for higher throughput)
        """
        if not self._bootstrap_servers:
            raise MessageBrokerError("KafkaManager is not configured. Call setup() first.")

        if self._producer is None:
            logger.info("Initializing Kafka producer...")
            try:
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=self._bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    # Durability settings
                    acks='all',  # Ensure messages are acknowledged by all in-sync replicas

                    # Performance optimizations
                    linger_ms=5,  # Wait 5ms to batch messages (reduces network calls)
                    max_batch_size=32768,  # 32KB batch size (default 16KB)
                    compression_type='gzip',  # Compress messages to reduce bandwidth

                    # Retry settings
                    retry_backoff_ms=100,
                )
                await self._producer.start()
                logger.info("Kafka producer started successfully.")
            except AIOKafkaError as e:
                logger.error(f"Failed to connect Kafka producer: {e}")
                self._producer = None  # Reset on failure
                raise KafkaConnectionError(f"Failed to connect Kafka producer: {e}") from e
        return self._producer

    def create_consumer(self, *topics, group_id: str, **kwargs) -> AIOKafkaConsumer:
        """
        Creates and returns a new AIOKafkaConsumer instance for the given topics.
        The consumer is NOT started automatically. The caller is responsible for
        starting and stopping the consumer.
        """
        if not self._bootstrap_servers:
            raise ConnectionError("KafkaManager is not configured. Call setup() first.")

        logger.info(f"Creating Kafka consumer for topics {topics} in group '{group_id}'")
        return AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self._bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset='earliest',  # Start reading from the beginning of the topic if no offset is stored
            **kwargs
        )

    async def close(self):
        """
        Stops the singleton producer if it has been initialized.
        """
        if self._producer:
            logger.info("Stopping Kafka producer...")
            await self._producer.stop()
            self._producer = None
            logger.info("Kafka producer stopped.")


# A single, shared instance for the entire application
kafka_manager = KafkaManager()
