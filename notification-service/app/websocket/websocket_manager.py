import asyncio
import json
from typing import Dict, Set
from sanic import Websocket


class WebSocketManager:
    """
    Manages WebSocket connections for real-time notifications.
    Maps user IDs to their active WebSocket connections.
    """

    def __init__(self):
        self.user_connections: Dict[str, Set[Websocket]] = {}  # user_id -> connections
        self.lock = asyncio.Lock()

    # ===== User =====

    async def connect_to_user(self, websocket: Websocket, user_id: str):
        """Register a new WebSocket connection for a user."""
        async with self.lock:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)


    async def disconnect_from_user(self, websocket: Websocket, user_id: str):
        """Unregister a WebSocket connection for a user."""
        async with self.lock:
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:  # Remove empty sets
                    del self.user_connections[user_id]


    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to all WebSocket connections of a specific user."""
        json_message = json.dumps(message, ensure_ascii=False)
        websockets_to_send = []

        async with self.lock:
            if user_id in self.user_connections:
                websockets_to_send = list(self.user_connections[user_id])

        if not websockets_to_send:
            return

        disconnected = set()
        for ws in websockets_to_send:
            try:
                # Gửi thẳng, nếu kết nối đã đóng Sanic sẽ ném Exception
                await ws.send(json_message)
            except Exception as e:
                disconnected.add(ws)

        if disconnected:
            async with self.lock:
                if user_id in self.user_connections:
                    for ws in disconnected:
                        self.user_connections[user_id].discard(ws)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]


    def get_user_connections_count(self, user_id: str) -> int:
        """Get the number of active connections for a user."""
        return len(self.user_connections.get(user_id, set()))


    async def disconnect_user_all_connections(self, user_id: str):
        """Disconnect all WebSocket connections for a user."""
        websockets_to_close = []
        async with self.lock:
            if user_id in self.user_connections:
                # Copy list for closing outside lock
                websockets_to_close = list(self.user_connections[user_id])
                
                # Cleanup internal state immediately
                del self.user_connections[user_id]

        # Perform I/O outside lock
        for ws in websockets_to_close:
            try:
                await ws.close()
            except Exception as e:
                pass

    def get_total_connections(self) -> int:
        """Get the total number of active connections."""
        user_conn_count = sum(len(connections) for connections in self.user_connections.values())
        return user_conn_count


# Global WebSocket manager instance
websocket_manager = WebSocketManager()