# shopping_shared/sanic/error_handler.py
from sanic import Sanic, Request, response
from pydantic import ValidationError

# Import the shared exceptions
from shopping_shared import exceptions as shared_exceptions
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Error Handler")

def register_shared_error_handlers(app: Sanic):
    """
    Registers a set of shared, standardized error handlers for a Sanic application.
    This function should be called during the app creation process.
    """

    @app.exception(shared_exceptions.SharedAppException)
    async def handle_shared_app_exception(request: Request, exc: shared_exceptions.SharedAppException):
        """
        Handles all known, intentional application exceptions defined in the shared package.
        """
        headers = {}
        # Special handling for TooManyRequests to include the Retry-After header
        if isinstance(exc, shared_exceptions.TooManyRequests) and exc.retry_after:
            headers["Retry-After"] = str(exc.retry_after)

        # Log the handled exception for visibility, but at a lower level (e.g., INFO or WARNING)
        logger.info(f"Handled exception for request {request.path}: {exc.__class__.__name__} (Status: {exc.status_code}) - {exc}")

        return response.json(
            {"status": "fail", "message": str(exc)},
            status=exc.status_code,
            headers=headers
        )

    @app.exception(ValidationError)
    async def handle_pydantic_validation_error(request: Request, exc: ValidationError):
        """
        Handles Pydantic validation errors, which are common in request validation.
        Returns a 422 Unprocessable Entity response.
        """
        logger.warning(f"Validation error for request {request.path}: {exc.errors()}")
        return response.json(
            {
                "status": "fail",
                "message": "Request validation failed.",
                "data": exc.errors()
            },
            status=422
        )

    @app.exception(Exception)
    async def handle_generic_exception(request: Request, exc: Exception):
        """
        Handles all other unexpected exceptions, treating them as 500 Internal Server Errors.
        Logs the full error for debugging but returns a generic message to the client.
        """
        logger.error(f"Unexpected server error on request {request.path}: {exc}", exc_info=exc)

        return response.json(
            {
                "status": "error",
                "message": "An internal server error occurred. The technical team has been notified."
            },
            status=500
        )

    logger.info("Shared error handlers have been registered.")
