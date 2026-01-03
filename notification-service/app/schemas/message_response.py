from shopping_shared.schemas.base_schema import BaseSchema

class MessageResponse(BaseSchema):
    event_type: str
    data: dict = None
