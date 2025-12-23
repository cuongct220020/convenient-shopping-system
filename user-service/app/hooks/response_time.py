# user-service/app/hooks/response_time.py
import time
from typing import Any, Optional

from sanic import Request
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger('Response Time Middleware')


async def add_start_time(request: Request) -> None:
    # Store start time in request context to avoid mutating headers
    request.ctx.start_time = time.time()


async def add_spent_time(request: Request, response: Any) -> None:
    # Compute elapsed time from ctx and log with appropriate level
    try:
        timestamp: Optional[float] = getattr(request.ctx, "start_time", None)
        if timestamp is None:
            return

        spend_time = round((time.time() - float(timestamp)), 3)
        # Ensure header values are strings
        response.headers['latency'] = str(spend_time)

        # Build a concise log message
        msg = "{status} {method} {path} {query} {latency}s".format(
            status=response.status,
            method=request.method,
            path=request.path,
            query=request.query_string,
            latency=spend_time
        )

        # Log according to response status
        if response.status >= 400:
            logger.error(msg)
        elif response.status >= 300:
            logger.warning(msg)
        else:
            logger.info(msg)

    except Exception as ex:
        # Log exception but do not raise to avoid interrupting request response flow
        logger.exception("Failed to compute or log response time: %s", ex)
