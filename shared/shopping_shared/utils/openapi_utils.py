from typing import Any, Dict, Type
from pydantic import BaseModel, TypeAdapter

def get_pydantic_schema(model: Any) -> Dict[str, Any]:
    """
    Sinh ra JSON Schema chuẩn từ Pydantic V2 Model để dùng cho OpenAPI.
    
    Hàm này thực hiện:
    1. Gọi `model_json_schema()` (chuẩn Pydantic V2).
    2. Loại bỏ trường `model_config` thừa nếu nó bị lọt vào danh sách properties.
    
    Args:
        model: Pydantic Model class OR any supported type (e.g. List[MyModel]) for TypeAdapter.
        
    Returns:
        Dict: JSON Schema dictionary.
    """
    # Pydantic v2:
    # - BaseModel classes support .model_json_schema()
    # - For typing constructs like List[MyModel], use TypeAdapter(...).json_schema()
    if hasattr(model, "model_json_schema"):
        schema = model.model_json_schema()
    else:
        schema = TypeAdapter(model).json_schema()
    
    # Clean up: Xóa model_config nếu tồn tại trong properties
    if "properties" in schema and "model_config" in schema["properties"]:
        del schema["properties"]["model_config"]
        
    return schema

def get_openapi_body(model: Any, content_type: str = "application/json") -> Dict[str, Any]:
    """
    Helper trả về cấu trúc 'body' chuẩn cho @openapi.definition.
    
    Ví dụ dùng:
    @openapi.definition(
        body=get_openapi_body(MyModel)
    )
    """
    return {content_type: get_pydantic_schema(model)}