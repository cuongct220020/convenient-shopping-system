import asyncio
from typing import Dict, Set
from sanic import Websocket
from shopping_shared.utils.logger_utils import get_logger


logger = get_logger("WebSocket Manager")


class WebSocketManager:
    """
    Manages WebSocket connections for real-time notifications.
    Maps user IDs to their active WebSocket connections.
    """
    
    def __init__(self):
        self.user_connections: Dict[str, Set[Websocket]] = {}  # user_id -> connections
        self.group_connections: Dict[str, Set[Websocket]] = {}
        self.lock = asyncio.Lock()

    # ===== User =====

    async def connect_to_user(self, websocket: Websocket, user_id: str):
        """Register a new WebSocket connection for a user."""
        async with self.lock:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
            logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.user_connections[user_id])}")


    async def disconnect_from_user(self, websocket: Websocket, user_id: str):
        """Unregister a WebSocket connection for a user."""
        async with self.lock:
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:  # Remove empty sets
                    del self.user_connections[user_id]
                logger.info(f"WebSocket disconnected for user {user_id}. Remaining connections: {len(self.user_connections.get(user_id, set()))}")


    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to all WebSocket connections of a specific user."""
        async with self.lock:
            if user_id in self.user_connections:
                disconnected = set()
                for ws in self.user_connections[user_id].copy():
                    try:
                        await ws.send(message)
                        logger.debug(f"Sent message to user {user_id}: {message}")
                    except Exception as e:
                        logger.error(f"Failed to send message to user {user_id}: {e}")
                        disconnected.add(ws)
                
                # Clean up disconnected connections
                for ws in disconnected:
                    self.user_connections[user_id].discard(ws)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]

    # ===== Family Group =====

    async def connect_to_group(self, websocket: Websocket, group_id: str):
        async with self.lock:
            if group_id not in self.group_connections:
                self.group_connections[group_id] = set()
            self.group_connections[group_id].add(websocket)
            logger.info(f"Websocket connected to group: {group_id}. Total connections: {len(self.group_connections.get(group_id, set()))}")

    async def disconnect_from_group(self, websocket: Websocket, group_id: str):
        """Unregister a WebSocket connection for a group."""
        async with self.lock:
            if group_id in self.group_connections:
                self.group_connections[group_id].discard(websocket)
                if not self.group_connections[group_id]:
                    del self.group_connections[group_id]
                logger.info(f"WebSocket disconnected from group {group_id}. Remaining connections: {len(self.group_connections.get(group_id, set()))}")


    async def broadcast_to_group(self, group_id: str, message: dict):
        """Send a message to all WebSocket connections of multiple users."""
        async with self.lock:
            if group_id in self.group_connections:
                disconnected = set()

                for ws in self.group_connections[group_id].copy():
                    try:
                        await ws.send(message)
                    except Exception as e:
                        logger.error(f"Failed to send message to group {group_id}: {e}")
                        disconnected.add(ws)

            for ws in disconnected:
                self.group_connections[group_id].discard(ws)
            if not self.group_connections[group_id]:
                del self.group_connections[group_id]


    def get_user_connections_count(self, user_id: str) -> int:
        """Get the number of active connections for a user."""
        return len(self.user_connections.get(user_id, set()))


    def get_group_connections_count(self, group_id: str) -> int:
        return len(self.group_connections.get(group_id, set()))


    def get_total_connections(self) -> int:
        """Get the total number of active connections."""
        user_conn_count = sum(len(connections) for connections in self.user_connections.values())
        group_conn_count = sum(len(connections) for connections in self.group_connections.values())
        return user_conn_count + group_conn_count


# Global WebSocket manager instance
websocket_manager = WebSocketManager()