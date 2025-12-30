# user-service/app/hooks/request_context.py
from sanic.request import Request
from sanic.response import BaseHTTPResponse
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Security Headers Middleware")

class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.
    Kong Gateway doesn't automatically add these headers,
    so service must handle them at application level.
    """

    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    }

    @staticmethod
    async def add_security_headers(_: Request, response: BaseHTTPResponse) -> None:
        """Apply security headers to response"""
        for header, value in SecurityHeadersMiddleware.SECURITY_HEADERS.items():
            response.headers[header] = value
