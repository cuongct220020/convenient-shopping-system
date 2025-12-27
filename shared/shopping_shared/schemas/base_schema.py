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
