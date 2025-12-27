# user-service/app/decorators/__init__.py
"""
Decorators for User Service endpoints with OpenAPI documentation support.

Decorators:
- validate_request: Validate request body against Pydantic schema
- idempotent: Ensure idempotent POST/PATCH requests
- require_system_role: Check system-level role (ADMIN, USER)
- require_group_role: Check role within a specific family group
- api_response: Document API responses for OpenAPI
"""

from .validate_request import validate_request
from .idempotency import idempotent
from .require_system_role import require_system_role
from .require_group_role import require_group_role

__all__ = [
    # Decorators
    "validate_request",
    "idempotent", 
    "require_system_role",
    "require_group_role",
]