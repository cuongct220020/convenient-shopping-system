# python
# File: `shared/shopping_shared/caching/redis_manager.py`
import asyncio
from typing import Optional

from redis.asyncio import Redis, ConnectionPool
from shopping_shared.exceptions import CacheError
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Redis Manager")


class RedisManager:
    """A manager for the Redis connection pool, designed for common use."""

    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self._client: Optional[Redis] = None
        self._available: bool = False

    async def setup(
            self,
            host: str,
            port: int,
            db: int,
            password: Optional[str],
            decode_responses: bool = True,
            max_retries: int = 3,
            retry_delay: float = 1.0,
            backoff: float = 2.0
    ) -> None:
        """
        Creates the connection pool and verifies connectivity with retries.
        Does not raise on final failure; sets availability flag instead.
        """
        try:
            # create connection pool and client
            self.pool = ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses
            )
            self._client = Redis(connection_pool=self.pool)
            logger.info(f"Redis connection pool initialized: {host}:{port}, db={db}")
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection pool: {e}")
            # ensure we mark unavailable and return
            self._available = False
            return

        # try pinging with retries
        delay = retry_delay
        for attempt in range(1, max_retries + 1):
            try:
                await self._client.ping()
                self._available = True
                logger.info("Redis ping successful; redis available.")
                return
            except Exception as e:
                logger.warning(f"Redis ping attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(delay)
                    delay *= backoff
                else:
                    logger.error("All Redis ping attempts failed; continuing without Redis.")
                    self._available = False

    async def close(self) -> None:
        """Closes the connection pool."""
        try:
            if self._client:
                await self._client.close()
                logger.debug("Redis client closed.")
                self._client = None
            if self.pool:
                await self.pool.disconnect()
                logger.info("Redis connection pool disconnected.")
                self.pool = None
        except Exception as e:
            logger.error(f"Error occurred while closing Redis connection: {e}")
        finally:
            self._available = False

    @property
    def client(self) -> Redis:
        """
        Provides a cached, reusable Redis client from the connection pool.
        Raises CacheError if Redis is not available.
        """
        if not self._available or not self._client:
            logger.error("Redis not available. Call setup() and ensure successful connection first.")
            raise CacheError("Redis not available.")
        return self._client

    def is_available(self) -> bool:
        """Return whether Redis is currently available."""
        return bool(self._available)


# A single, shared instance for the entire application
redis_manager = RedisManager()