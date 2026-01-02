# shared/shopping_shared/exceptions.py

class SharedAppException(Exception):
    """
    Base class for all shared, application-specific exceptions.
    It's framework-agnostic but contains HTTP-relevant information.
    """
    status_code: int = 500
    message: str = "An internal server error occurred."

    def __init__(self, message: str | None = None, **kwargs):
        # If a custom message is provided, use it. Otherwise, use the class's default.
        super().__init__(message or self.message)
        # Allow storing extra context if needed
        self.extra_data = kwargs


# --- Framework-agnostic HTTP-like exceptions ---

class BadRequest(SharedAppException):
    """Status: 400 Bad Request"""
    status_code = 400
    message = "The request was malformed or invalid."


class Unauthorized(SharedAppException):
    """Status: 401 Unauthorized"""
    status_code = 401
    message = "Authentication is required and has failed or has not yet been provided."


class Forbidden(SharedAppException):
    """Status: 403 Forbidden"""
    status_code = 403
    message = "You do not have permission to perform this action."


class NotFound(SharedAppException):
    """Status: 404 Not Found"""
    status_code = 404
    message = "The requested resource was not found."


class Conflict(SharedAppException):
    """Status: 409 Conflict"""
    status_code = 409
    message = "A conflict occurred with the current state of the resource."


class UnprocessableEntity(SharedAppException):
    """Status: 422 Unprocessable Entity"""
    status_code = 422
    message = "The request was well-formed but was unable to be followed due to semantic errors."


class TooManyRequests(SharedAppException):
    """Status: 429 Too Many Requests"""
    status_code = 429
    message = "Too many requests have been made in a given amount of time."

    def __init__(self, message: str | None = None, retry_after: int | None = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


# --- Internal Logic Exceptions ---

class ServerError(SharedAppException):
    """Status: 500 Server Error"""
    status_code = 500
    message = "An internal server error occurred."

class DatabaseError(SharedAppException):
    """Raised for database-related errors."""
    status_code = 503
    message = "A database error occurred."


class CacheError(SharedAppException):
    """Raised for cache-related errors (e.g., Redis)."""
    status_code = 503
    message = "A cache service error occurred."


class MessageBrokerError(SharedAppException):
    """Raised for message broker-related errors (e.g., Kafka)."""
    status_code = 503
    message = "A message broker service error occurred."


class KafkaConnectionError(SharedAppException):
    """Raised specifically for Kafka connection issues."""
    status_code = 503
    message = "Failed to connect to Kafka."