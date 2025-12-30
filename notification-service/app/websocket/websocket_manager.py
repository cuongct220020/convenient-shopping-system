import asyncio
from typing import Dict, Set
from sanic import Websocket
from uuid import UUID
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("WebSocket Manager")


class WebSocketManager:
    """
    Manages WebSocket connections for real-time notifications.
    Maps user IDs to their active WebSocket connections.
    """
    
    def __init__(self):
        self.connections: Dict[str, Set[Websocket]] = {}  # user_id -> set of connections
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: Websocket, user_id: str):
        """Register a new WebSocket connection for a user."""
        async with self.lock:
            if user_id not in self.connections:
                self.connections[user_id] = set()
            self.connections[user_id].add(websocket)
            logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.connections[user_id])}")
    
    async def disconnect(self, websocket: Websocket, user_id: str):
        """Unregister a WebSocket connection for a user."""
        async with self.lock:
            if user_id in self.connections:
                self.connections[user_id].discard(websocket)
                if not self.connections[user_id]:  # Remove empty sets
                    del self.connections[user_id]
                logger.info(f"WebSocket disconnected for user {user_id}. Remaining connections: {len(self.connections.get(user_id, set()))}")
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to all WebSocket connections of a specific user."""
        async with self.lock:
            if user_id in self.connections:
                disconnected = set()
                for ws in self.connections[user_id].copy():
                    try:
                        await ws.send_json(message)
                        logger.debug(f"Sent message to user {user_id}: {message}")
                    except Exception as e:
                        logger.error(f"Failed to send message to user {user_id}: {e}")
                        disconnected.add(ws)
                
                # Clean up disconnected connections
                for ws in disconnected:
                    self.connections[user_id].discard(ws)
                if not self.connections[user_id]:
                    del self.connections[user_id]
    
    async def broadcast_to_group(self, user_ids: list, message: dict):
        """Send a message to all WebSocket connections of multiple users."""
        for user_id in user_ids:
            await self.send_to_user(user_id, message)
    
    def get_user_connections_count(self, user_id: str) -> int:
        """Get the number of active connections for a user."""
        return len(self.connections.get(user_id, set()))
    
    def get_total_connections(self) -> int:
        """Get the total number of active connections."""
        return sum(len(connections) for connections in self.connections.values())


# Global WebSocket manager instance
websocket_manager = WebSocketManager()