# user-service/app/decorators/validate_request.py
from functools import wraps
from typing import Type

from pydantic import ValidationError
from sanic.request import Request
from sanic.response import json
from sanic_ext import openapi

# Import the standardized response schema
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.schemas.base_schema import BaseSchema
from shopping_shared.sanic.schemas import DocGenericResponse
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Validate Request Decorator")

def validate_request(schema: Type[BaseSchema], auto_document: bool = True):
    """
    A decorator that automatically validates the request body against a Pydantic schema.

    On success, it attaches the validated data to `request.ctx.validated_data`.
    On failure, it returns a 400 Bad Request or 422 Unprocessable Entity using the standardized GenericResponse format.

    Args:
        schema: The Pydantic schema to validate against
        auto_document: Whether to automatically document OpenAPI responses (default: True)
    """
    def decorator(func):
        if auto_document:
            # Automatically document the possible validation error responses
            func = openapi.response(400, DocGenericResponse, "Bad Request - Invalid JSON")(func)
            func = openapi.response(422, DocGenericResponse, "Validation Error")(func)

        @wraps(func)
        async def decorated_function(view, request: Request, *args, **kwargs):
            if not request.json:
                error_response = GenericResponse(
                    status="fail",
                    message="Invalid request: body is empty or not valid JSON."
                )
                return json(error_response.model_dump(exclude_none=True), status=400)

            try:
                validated_data = schema.model_validate(request.json)
                request.ctx.validated_data = validated_data
            except ValidationError as error:
                # Capture the error details
                error_details = [{"loc": e["loc"], "msg": e["msg"]} for e in error.errors()]

                # Use GenericResponse for a consistent error structure
                error_response = GenericResponse(
                    status="fail",
                    message=f"Validation error for {schema.__name__}",
                    data=error_details
                )

                return json(error_response.model_dump(exclude_none=True), status=422)

            return await func(view, request, *args, **kwargs)
        return decorated_function
    return decorator
