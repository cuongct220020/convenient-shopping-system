# shared/shopping_shared/messaging/kafka_manager.py

import json
from typing import Optional, List, Any, Dict

try:
    import orjson
except ImportError:
    orjson = None

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
        self._consumers: List[AIOKafkaConsumer] = []
        self._bootstrap_servers: str = ""

    @property
    def bootstrap_servers(self) -> Optional[str]:
        """Returns the configured bootstrap servers, or None if not configured."""
        return self._bootstrap_servers if self._bootstrap_servers else None

    def setup(self, bootstrap_servers: str):
        """
        Stores the Kafka bootstrap servers configuration.
        """
        if not bootstrap_servers:
            raise ValueError("Kafka bootstrap servers must be provided.")
        self._bootstrap_servers = bootstrap_servers
        logger.info(f"KafkaManager setup with bootstrap servers: {bootstrap_servers}")

    @staticmethod
    def _serializer(value: Any) -> bytes:
        if orjson:
            return orjson.dumps(value)
        return json.dumps(value).encode('utf-8')

    @staticmethod
    def _deserializer(value: bytes) -> Any:
        if value is None:
            return None
        if orjson:
            return orjson.loads(value)
        return json.loads(value.decode('utf-8'))

    async def get_producer(self) -> AIOKafkaProducer:
        """
        Initializes and returns a singleton AIOKafkaProducer instance.
        The producer is started on its first retrieval.

        Performance optimizations:
        - linger_ms: Batch messages for 5ms before sending (reduces network calls)
        - batch_size: Max bytes per batch (default 16KB, increased to 32KB)
        - compression_type: gzip compression reduces network bandwidth
        - acks='all': Ensures durability (can use acks=1 for higher throughput)
        - enable_idempotence=True: Ensures exactly-once delivery and ordering.
        """
        if not self._bootstrap_servers:
            raise MessageBrokerError("KafkaManager is not configured. Call setup() first.")

        if self._producer is None:
            logger.info("Initializing Kafka producer...")
            try:
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=self._bootstrap_servers,
                    value_serializer=self._serializer,
                    # Durability settings
                    acks='all',  # Ensure messages are acknowledged by all in-sync replicas
                    enable_idempotence=True,

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

    async def send_message(
        self,
        topic: str,
        value: Any,
        key: str = None,
        headers: Dict[str, str] = None,
        wait: bool = True
    ):
        """
        Sends a message to Kafka safely with logging and headers support.

        :param topic: Kafka topic to send to.
        :param value: The message body (will be serialized).
        :param key: Optional key for partitioning (ensures ordering).
        :param headers: Optional dictionary of headers.
        :param wait: If True, waits for broker acknowledgement (Slower, Safer).
                     If False, returns immediately after buffering (Faster, riskier).
        """
        producer = await self.get_producer()
        try:
            key_bytes = key.encode('utf-8') if key else None
            # Convert dict headers to list of tuples for aiokafka
            kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()] if headers else None

            if wait:
                # Slower but safer (Inventory, Payments)
                await producer.send_and_wait(
                    topic=topic,
                    value=value,
                    key=key_bytes,
                    headers=kafka_headers
                )
            else:
                # Faster, fire-and-forget (Analytics, Logs)
                await producer.send(
                    topic=topic,
                    value=value,
                    key=key_bytes,
                    headers=kafka_headers
                )
        except AIOKafkaError as e:
            logger.error(f"Failed to send message to topic {topic}: {e}")
            raise MessageBrokerError(f"Failed to send message: {e}") from e

    def create_consumer(self, *topics, group_id: str, **kwargs) -> AIOKafkaConsumer:
        """
        Creates and returns a new AIOKafkaConsumer instance for the given topics.
        The consumer is NOT started automatically. The caller is responsible for
        starting and stopping the consumer.
        """
        if not self._bootstrap_servers:
            raise ConnectionError("KafkaManager is not configured. Call setup() first.")

        logger.info(f"Creating Kafka consumer for topics {topics} in group '{group_id}'")
        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self._bootstrap_servers,
            group_id=group_id,
            value_deserializer=self._deserializer,
            auto_offset_reset='earliest',  # Start reading from the beginning of the topic if no offset is stored
            **kwargs
        )
        self._consumers.append(consumer)
        return consumer

    async def close(self):
        """
        Stops the singleton producer and all tracked consumers.
        """
        logger.info("Stopping Kafka Manager...")

        # 1. Stop Producer
        if self._producer:
            try:
                await self._producer.stop()
                self._producer = None
                logger.info("Kafka producer stopped.")
            except Exception as e:
                logger.error(f"Error stopping producer: {e}")

        # 2. Stop All Consumers
        for i, consumer in enumerate(self._consumers):
            try:
                await consumer.stop()
                logger.info(f"Kafka consumer {i+1} stopped.")
            except Exception as e:
                logger.error(f"Error stopping consumer {i+1}: {e}")
        self._consumers.clear()


# A single, shared instance for the entire application
kafka_manager = KafkaManager()
