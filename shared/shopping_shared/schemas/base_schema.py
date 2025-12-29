# shared/shopping_shared/schemas/base_schema.py
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """
    A base schema for all other schemas in the application.
    It includes a common configuration.
    """
    model_config = ConfigDict(
        from_attributes=True,
        extra='forbid',
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True
    )

    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        kwargs.setdefault("ref_template", "#/components/schemas/{model}")
        schema = super().model_json_schema(*args, **kwargs)
        if "properties" in schema:
            schema["properties"].pop("model_config", None)
            schema["properties"].pop("config_dict", None)
        return schema

    @classmethod
    def schema(cls, *args, **kwargs):
        schema = super().schema(*args, **kwargs)
        if "properties" in schema:
            schema["properties"].pop("model_config", None)
            schema["properties"].pop("config_dict", None)
        return schema
