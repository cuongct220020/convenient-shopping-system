# user-service/app/hooks/response_time.py
import time
from typing import Optional

from sanic import Request
from sanic.response import BaseHTTPResponse
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Response Time Middleware")

class ResponseTimeMiddleware:
    """
    Track request processing time and log structured metrics.
    Provides service-level performance monitoring after Kong Gateway.
    """

    def __init__(self, slow_request_threshold_ms: float = 1000.0):
        """
        Initialize middleware with custom logger and performance threshold.
        """
        self.slow_threshold_ms = slow_request_threshold_ms

    @staticmethod
    async def before_request(request: Request) -> None:
        """Store request start time using high-precision timer"""
        request.ctx.start_time = time.perf_counter()

    async def after_request(self, request: Request, response: BaseHTTPResponse) -> None:
        """Calculate latency and add structured logging with performance alerts"""
        start_time: Optional[float] = getattr(request.ctx, "start_time", None)
        if start_time is None:
            return

        try:
            # Calculate latency in milliseconds
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Add latency header for debugging
            response.headers['X-Response-Time'] = f"{latency_ms}ms"

            # Extract user context for logging (injected by auth middleware)
            user_context = getattr(request.ctx, 'user', {})
            user_id = user_context.get('user_id', 'anonymous')

            # Build structured log data
            log_data = {
                'method': request.method,
                'path': request.path,
                'status': response.status,
                'latency_ms': latency_ms,
                'user_id': user_id,
                'query': request.query_string or '',
            }

            # Log based on status code and performance
            if response.status >= 500:
                logger.error("Server error occurred", extra=log_data)
            elif response.status >= 400:
                logger.warning("Client error", extra=log_data)
            elif latency_ms > self.slow_threshold_ms:
                logger.warning("Slow request detected", extra=log_data)
            else:
                logger.info("Request completed", extra=log_data)

        except Exception as ex:
            # Don't let logging failures interrupt response flow
            logger.exception("Failed to compute response time: %s", ex)
