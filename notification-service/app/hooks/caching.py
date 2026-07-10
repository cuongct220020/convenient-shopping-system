import asyncio
from sanic import Sanic, Request
from shopping_shared.caching.redis_manager import redis_manager
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.exceptions import CacheError

logger = get_logger("Caching Middleware")


async def setup_redis(app: Sanic):
    """Hook to initialize the Redis connection pool with graceful handling."""
    logger.info("Initializing Redis connection pool...")

    # Redis Configuration
    redis_host = app.config.REDIS.REDIS_HOST
    redis_port = app.config.REDIS.REDIS_PORT
    redis_db = app.config.REDIS.REDIS_DB
    redis_password = app.config.REDIS.REDIS_PASSWORD
    decode_responses = app.config.REDIS.REDIS_DECODE_RESPONSES

    # Await setup and allow the manager to handle retries and availability flag.
    await redis_manager.setup(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password,
        decode_responses=decode_responses,
        max_connections=getattr(app.config.REDIS, "REDIS_MAX_CONNECTIONS", 10),
        socket_timeout=getattr(app.config.REDIS, "REDIS_SOCKET_TIMEOUT", 5.0),
    )

    if redis_manager.is_available():
        logger.info(f"Redis connection pool successfully created at {redis_host}:{redis_port}.")
    else:
        # Do not raise here; allow application to start without Redis.
        logger.warning("Redis is unavailable. The application will continue in degraded mode.")


async def close_redis(_app: Sanic):
    """Hook to close the Redis connection pool."""
    logger.info("Closing Redis connection pool...")
    try:
        # Close the Redis manager with timeout
        await asyncio.wait_for(redis_manager.close(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.warning("Redis manager close operation timed out, forcing shutdown")
        # Force close without waiting
        try:
            redis_manager.close()
        except:
            pass  # Ignore errors during force close
    except Exception as e:
        logger.error(f"Error during Redis manager shutdown: {e}")
    logger.info("Redis connection pool closed.")


async def inject_redis_client(request: Request):
    """
    Injects the shared Redis client into the request context.
    If Redis is unavailable, inject None so handlers can handle fallback logic.
    """
    try:
        if redis_manager.is_available():
            request.ctx.redis_client = redis_manager.client
        else:
            request.ctx.redis_client = None
    except CacheError:
        request.ctx.redis_client = None