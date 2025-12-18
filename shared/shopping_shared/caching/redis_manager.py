# shared/shopping_shared/caching/redis_manager.py
from redis.asyncio import Redis, ConnectionPool
from shopping_shared.exceptions import CacheError

from shopping_shared.utils.logger_utils import get_logger

logger = get_logger(__name__)

class RedisManager:
    """A manager for the Redis connection pool, designed for common use."""

    def __init__(self):
        self.pool: ConnectionPool | None = None
        self._client: Redis | None = None

    def setup(
            self,
            host: str,
            port: int,
            db: int,
            password: str,
            decode_responses: bool = True
    ):
        """Creates the connection pool."""
        try:
            self.pool = ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses
            )
            logger.info(f"Redis connection pool initialized: {host}:{port}, db={db}")
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection pool: {e}")
            raise

    async def close(self):
        """Closes the connection pool."""
        try:
            if self._client:
                await self._client.close()
                logger.debug("Redis client closed.")
            if self.pool:
                await self.pool.disconnect()
                logger.info("Redis connection pool disconnected.")
        except Exception as e:
            logger.error(f"Error occurred while closing Redis connection: {e}")

    @property
    def client(self) -> Redis:
        """
        Provides a cached, reusable Redis client from the connection pool.
        The connection pool handles the underlying connection management.
        """
        if not self.pool:
            logger.error("Redis connection pool not initialized. Call setup() first.")
            raise CacheError("Redis connection pool not initialized. Call setup() first.")
        if not self._client:
            self._client = Redis(connection_pool=self.pool)
            logger.debug("Redis client created from pool.")
        return self._client


# A single, shared instance for the entire application
redis_manager = RedisManager()
