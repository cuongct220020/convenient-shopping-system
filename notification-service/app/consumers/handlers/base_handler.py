# notification-service/app/consumers/handlers/base_handler.py
from abc import ABC, abstractmethod

class BaseMessageHandler(ABC):
    """Abstract Base Class for Kafka Message Handlers."""
    
    @abstractmethod
    async def handle(self, message_value: dict, app):
        """
        Process the message.
        :param message_value: Deserialized JSON body of the message.
        :param app: Sanic app instance (to access services like email_service).
        """
        pass
