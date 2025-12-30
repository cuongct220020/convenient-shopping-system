# user-service/app/hooks/__init__.py
"""
Hooks and Middlewares for User Service

Provides:
- SecurityHeadersMiddleware: Add security headers to all responses
- ResponseTimeMiddleware: Track request latency and log structured metrics
"""

from .request_context import SecurityHeadersMiddleware
from .response_time import ResponseTimeMiddleware

__all__ = [
    'SecurityHeadersMiddleware',
    'ResponseTimeMiddleware',
]

