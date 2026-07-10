from sanic.views import HTTPMethodView
from sanic.response import json

from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Base View")

class BaseAPIView(HTTPMethodView):
    """Base class cho các API view với helper methods"""
    
    @staticmethod
    def success_response(data=None, message="Success", status_code=200):
        """Trả về response thành công chuẩn"""
        response_data = GenericResponse(
            status="success",
            message=message,
            data=data
        )
        return json(response_data.model_dump(mode="json"), status=status_code)
    
    @staticmethod
    def fail_response(message="Request failed", data=None, status_code=400):
        """Trả về response thất bại chuẩn"""
        response_data = GenericResponse(
            status="fail",
            message=message,
            data=data
        )
        return json(response_data.model_dump(mode="json"), status=status_code)

    @staticmethod
    def error_response(message="Internal server error", data=None, status_code=500):
        """Trả về response lỗi chuẩn"""
        response_data = GenericResponse(
            status="error",
            message=message,
            data=data
        )
        return json(response_data.model_dump(mode="json"), status=status_code)

