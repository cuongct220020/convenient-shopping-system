import asyncio
import json
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
        # Track which user connections belong to which groups to avoid duplicates
        self.connection_to_groups: Dict[Websocket, Set[str]] = {}
        self.lock = asyncio.Lock()

    # ===== User =====

    async def connect_to_user(self, websocket: Websocket, user_id: str):
        """Register a new WebSocket connection for a user."""
        async with self.lock:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
            # Initialize the connection's group tracking
            if websocket not in self.connection_to_groups:
                self.connection_to_groups[websocket] = set()
            logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.user_connections[user_id])}")


    async def disconnect_from_user(self, websocket: Websocket, user_id: str):
        """Unregister a WebSocket connection for a user."""
        async with self.lock:
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:  # Remove empty sets
                    del self.user_connections[user_id]
                # Remove from group tracking
                if websocket in self.connection_to_groups:
                    del self.connection_to_groups[websocket]
                logger.info(f"WebSocket disconnected for user {user_id}. Remaining connections: {len(self.user_connections.get(user_id, set()))}")


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
                logger.debug(f"Sent to {user_id}")
            except Exception as e:
                logger.warning(f"Connection lost for {user_id}: {e}")
                disconnected.add(ws)

        if disconnected:
            async with self.lock:
                if user_id in self.user_connections:
                    for ws in disconnected:
                        self.user_connections[user_id].discard(ws)
                        self.connection_to_groups.pop(ws, None)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]

    # ===== Family Group =====

    async def connect_to_group(self, websocket: Websocket, group_id: str):
        async with self.lock:
            if group_id not in self.group_connections:
                self.group_connections[group_id] = set()
            self.group_connections[group_id].add(websocket)
            if websocket not in self.connection_to_groups:
                self.connection_to_groups[websocket] = set()
            self.connection_to_groups[websocket].add(group_id)
            logger.info(f"Websocket connected to group: {group_id}")


    async def disconnect_from_group(self, websocket: Websocket, group_id: str):
        """Unregister a WebSocket connection for a group."""
        async with self.lock:
            if group_id in self.group_connections:
                self.group_connections[group_id].discard(websocket)
                if websocket in self.connection_to_groups:
                    self.connection_to_groups[websocket].discard(group_id)
                if not self.group_connections[group_id]:
                    del self.group_connections[group_id]


    async def broadcast_to_group(self, group_id: str, message: dict):
        """Send a message to all WebSocket connections of a group."""
        json_message = json.dumps(message, ensure_ascii=False)
        websockets_to_send = []

        async with self.lock:
            if group_id in self.group_connections:
                websockets_to_send = list(self.group_connections[group_id])

        if not websockets_to_send:
            return

        disconnected = set()
        for ws in websockets_to_send:
            try:
                await ws.send(json_message)
            except Exception as err:
                logger.warning(f"Connection lost for {group_id}: {err}")
                disconnected.add(ws)

        if disconnected:
            async with self.lock:
                for ws in disconnected:
                    # Cleanup from this group and others
                    if ws in self.connection_to_groups:
                        for g_id in self.connection_to_groups[ws]:
                            if g_id in self.group_connections:
                                self.group_connections[g_id].discard(ws)
                        del self.connection_to_groups[ws]
                if group_id in self.group_connections and not self.group_connections[group_id]:
                    del self.group_connections[group_id]


    def get_user_connections_count(self, user_id: str) -> int:
        """Get the number of active connections for a user."""
        return len(self.user_connections.get(user_id, set()))


    async def add_user_to_group(self, user_id: str, group_id: str):
        """
        Add a user to a group WebSocket connection.
        This should be called when a user is added to a group and they have active WebSocket connections.
        """
        async with self.lock:
            # Find all WebSocket connections for the user
            if user_id in self.user_connections:
                user_websockets = self.user_connections[user_id].copy()

                # Add each of the user's WebSocket connections to the group
                for ws in user_websockets:
                    if group_id not in self.group_connections:
                        self.group_connections[group_id] = set()
                    self.group_connections[group_id].add(ws)
                    # Track which groups this connection belongs to
                    if ws not in self.connection_to_groups:
                        self.connection_to_groups[ws] = set()
                    self.connection_to_groups[ws].add(group_id)

                logger.info(f"Added user {user_id} with {len(user_websockets)} connections to group {group_id}")
            else:
                logger.info(f"User {user_id} has no active WebSocket connections to add to group {group_id}")


    async def remove_user_from_group(self, user_id: str, group_id: str):
        """
        Remove a user from a group WebSocket connection.
        This should be called when a user is removed from a group.
        """
        async with self.lock:
            # Find all WebSocket connections for the user
            if user_id in self.user_connections:
                user_websockets = self.user_connections[user_id].copy()

                # Remove each of the user's WebSocket connections from the group
                for ws in user_websockets:
                    if group_id in self.group_connections:
                        self.group_connections[group_id].discard(ws)
                    # Remove from connection's group tracking
                    if ws in self.connection_to_groups:
                        self.connection_to_groups[ws].discard(group_id)

                # Clean up empty group if needed
                if group_id in self.group_connections and not self.group_connections[group_id]:
                    del self.group_connections[group_id]

                logger.info(f"Removed user {user_id} with {len(user_websockets)} connections from group {group_id}")
            else:
                logger.info(f"User {user_id} has no active WebSocket connections to remove from group {group_id}")


    async def disconnect_user_all_connections(self, user_id: str):
        """Disconnect all WebSocket connections for a user."""
        websockets_to_close = []
        async with self.lock:
            if user_id in self.user_connections:
                # Copy list for closing outside lock
                websockets_to_close = list(self.user_connections[user_id])
                
                # Cleanup internal state immediately
                del self.user_connections[user_id]
                
                for ws in websockets_to_close:
                    if ws in self.connection_to_groups:
                        for group_id in self.connection_to_groups[ws]:
                            if group_id in self.group_connections:
                                self.group_connections[group_id].discard(ws)
                                if not self.group_connections[group_id]:
                                    del self.group_connections[group_id]
                        del self.connection_to_groups[ws]

        # Perform I/O outside lock
        for ws in websockets_to_close:
            try:
                await ws.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket connection for user {user_id}: {e}")

        if websockets_to_close:
            logger.info(f"Disconnected all {len(websockets_to_close)} WebSocket connections for user {user_id}")
        else:
            logger.info(f"User {user_id} has no active WebSocket connections to disconnect")


    def get_group_connections_count(self, group_id: str) -> int:
        return len(self.group_connections.get(group_id, set()))

    def get_total_connections(self) -> int:
        """Get the total number of active connections."""
        user_conn_count = sum(len(connections) for connections in self.user_connections.values())
        group_conn_count = sum(len(connections) for connections in self.group_connections.values())
        return user_conn_count + group_conn_count


# Global WebSocket manager instance
websocket_manager = WebSocketManager()