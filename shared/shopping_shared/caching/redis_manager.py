# shared/shopping_shared/caching/redis_manager.py`
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
            max_connections: int = 10,
            socket_timeout: float = 5.0
    ) -> None:
        """
        Creates the connection pool.
        Tries to verify connectivity, but does NOT permanently disable Redis on failure.
        Allows auto-reconnect attempts by the underlying client.
        """
        try:
            self.pool = ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                max_connections=max_connections,
                socket_timeout=socket_timeout,
                socket_keepalive=True,
                health_check_interval=30  # Auto-ping every 30s when connection is idle
            )
            self._client = Redis(connection_pool=self.pool)
            logger.info(f"Redis connection pool initialized: {host}:{port}, db={db}")
        except Exception as e:
            logger.error(f"Failed to initialize Redis config: {e}")
            self._available = False
            return

        # Initial connectivity check (Soft check)
        # We try to ping, if fail, we just log warning but keep client object alive
        # so it can try to reconnect later (auto-healing).
        try:
            await self._client.ping()
            self._available = True
            logger.info("Redis initial ping successful.")
        except Exception as e:
            logger.warning(f"Redis initial ping failed: {e}. App will start in degraded mode, but will retry connection on demand.")
            self._available = False  # Mark as currently unavailable, but client exists

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
        Raises CacheError only if Redis client is not initialized (setup not called).
        """
        if not self._client:
            logger.error("Redis client not initialized. Call setup() first.")
            raise CacheError("Redis not initialized.")
        return self._client

    def is_available(self) -> bool:
        """Return whether Redis is currently available."""
        return bool(self._available)


# A single, shared instance for the entire application
redis_manager = RedisManager()