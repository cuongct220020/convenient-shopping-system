# shopping_shared/sanic/error_handler.py
from sanic import Sanic, Request
from sanic.response import json
from pydantic import ValidationError
from sanic.exceptions import MethodNotAllowed, NotFound

# Import the shared exceptions
from shopping_shared import exceptions as shared_exceptions
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.schemas.response_schema import GenericResponse

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

        response = GenericResponse(
            status="fail",
            message=str(exc)
        )

        return json(response.model_dump(), status=exc.status_code, headers=headers)


    @app.exception(ValidationError)
    async def handle_pydantic_validation_error(request: Request, exc: ValidationError):
        """
        Handles Pydantic validation errors, which are common in request validation.
        Returns a 422 Unprocessable Entity response.
        """
        logger.warning(f"Validation error for request {request.path}: {exc.errors()}")

        response = GenericResponse(
            status="fail",
            message="Request validation failed.",
            data=exc.errors()
        )

        return json(response.model_dump(), status=422)

    @app.exception(MethodNotAllowed)
    async def handle_method_not_allowed(request: Request, exc: MethodNotAllowed):
        """Return 405 instead of 500 when method is not allowed."""
        logger.warning(f"Method not allowed {request.method} for {request.path}")
        response = GenericResponse(status="fail", message=str(exc))
        return json(response.model_dump(), status=405)

    @app.exception(NotFound)
    async def handle_not_found(request: Request, exc: NotFound):
        """Return 404 for unknown routes."""
        logger.info(f"Route not found: {request.path}")
        response = GenericResponse(status="fail", message="Route not found")
        return json(response.model_dump(), status=404)


    @app.exception(Exception)
    async def handle_generic_exception(request: Request, exc: Exception):
        """
        Handles all other unexpected exceptions, treating them as 500 Internal Server Errors.
        Logs the full error for debugging but returns a generic message to the client.
        """
        logger.error(f"Unexpected server error on request {request.path}: {exc}", exc_info=exc)

        response = GenericResponse(
            status="error",
            message="An internal server error occurred. The technical team has been notified."
        )

        return json(response.model_dump(), status=500)

    logger.info("Shared error handlers have been registered.")
