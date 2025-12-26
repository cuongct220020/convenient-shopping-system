from typing import Type, Optional, Dict, Any
from sanic_ext import openapi

from shopping_shared.sanic.schemas import DocGenericResponse


def api_response(
    success_schema: Type = DocGenericResponse,
    success_status: int = 200,
    success_description: str = "Success",
    include_standard_errors: bool = True,
    additional_responses: Optional[Dict[int, Any]] = None
):
    """
    API response decorator that focuses on OpenAPI documentation only.
    Exception handling is handled by the global error handlers in shared package.
    """
    def decorator(func):
        # Add success response
        func = openapi.response(success_status, success_schema, success_description)(func)

        # Add standard error responses if requested
        if include_standard_errors:
            func = openapi.response(400, DocGenericResponse, "Bad Request - Validation Error")(func)
            func = openapi.response(401, DocGenericResponse, "Unauthorized")(func)
            func = openapi.response(403, DocGenericResponse, "Forbidden")(func)
            func = openapi.response(404, DocGenericResponse, "Not Found")(func)
            func = openapi.response(422, DocGenericResponse, "Unprocessable Entity")(func)
            func = openapi.response(500, DocGenericResponse, "Internal Server Error")(func)

        # Add any additional custom responses
        if additional_responses:
            for status_code, response_info in additional_responses.items():
                if isinstance(response_info, tuple):
                    schema, description = response_info
                    func = openapi.response(status_code, schema, description)(func)
                else:
                    func = openapi.response(status_code, response_info)(func)

        return func
    return decorator