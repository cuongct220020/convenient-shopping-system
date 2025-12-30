from typing import Any, Dict, Type
from pydantic import BaseModel

def get_pydantic_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Sinh ra JSON Schema chuẩn từ Pydantic V2 Model để dùng cho OpenAPI.
    
    Hàm này thực hiện:
    1. Gọi `model_json_schema()` (chuẩn Pydantic V2).
    2. Loại bỏ trường `model_config` thừa nếu nó bị lọt vào danh sách properties.
    
    Args:
        model: Class Pydantic Model.
        
    Returns:
        Dict: JSON Schema dictionary.
    """
    # Lấy schema gốc từ Pydantic V2
    schema = model.model_json_schema()
    
    # Clean up: Xóa model_config nếu tồn tại trong properties
    if "properties" in schema and "model_config" in schema["properties"]:
        del schema["properties"]["model_config"]
        
    return schema

def get_openapi_body(model: Type[BaseModel], content_type: str = "application/json") -> Dict[str, Any]:
    """
    Helper trả về cấu trúc 'body' chuẩn cho @openapi.definition.
    
    Ví dụ dùng:
    @openapi.definition(
        body=get_openapi_body(MyModel)
    )
    """
    return {content_type: get_pydantic_schema(model)}