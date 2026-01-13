# Notification Service

## Overview

This service handles real-time notifications for the Convenient Shopping System. It consumes events from Kafka topics published by other services and delivers notifications to clients via:
- **WebSocket connections** for real-time push notifications
- **REST API endpoints** for retrieving, managing, and querying stored notifications
- **Database storage** for persistent notification history

The service supports multiple notification types including group management events, food expiration alerts, meal plan notifications, and OTP delivery.

## Architecture

### Components

1. **WebSocket Manager**: Manages active WebSocket connections per user
2. **Kafka Consumer**: Consumes messages from multiple Kafka topics and routes them to appropriate handlers
3. **Message Handlers**: Process specific event types and create notifications
4. **Notification Service**: Handles database operations for notifications
5. **REST API**: Provides endpoints for querying and managing notifications
6. **Email Service**: Sends OTP emails for registration, password reset, and email change

## WebSocket Endpoints

The service exposes WebSocket endpoints for real-time notifications. In a local development environment (via Kong Gateway), use:

*   **User Notifications:**
    *   URL: `ws://localhost:8000/ws/v2/notification-service/notifications/users/<user_id>`
    *   Usage: For receiving personal notifications for a specific user in real-time.

**Authentication:**
These endpoints are protected. You must provide a valid JWT token.
1.  **Header:** `Authorization: Bearer <YOUR_JWT_TOKEN>` (Recommended for generic clients)
2.  **Query Parameter:** Append `?jwt=<YOUR_JWT_TOKEN>` to the URL (Useful for browser/simple testing)

    *Example:* `ws://localhost:8000/ws/v2/notification-service/notifications/users/123e4567-e89b-12d3-a456-426614174000?jwt=eyJhbG...`

*Note: In production, these endpoints are accessed via WSS (secure WebSocket).*

## REST API Endpoints

All REST endpoints require JWT authentication via the `Authorization: Bearer <JWT_TOKEN>` header.

### Base URL
- Local: `http://localhost:8000/api/v2/notification-service`
- Production: `https://<gateway-host>/api/v2/notification-service`

### Endpoints

#### GET `/notifications/users/<user_id>`
- **Description**: Retrieve all notifications for a specific user, ordered by creation date (newest first)
- **Path Parameters**:
  - `user_id` (UUID): The user ID whose notifications to retrieve
- **Response**: List of `NotificationResponseSchema` objects
- **Status Codes**: 
  - `200 OK`: Successfully retrieved notifications
  - `400 Bad Request`: Invalid user_id parameter
  - `403 Forbidden`: User cannot access another user's notifications
  - `500 Internal Server Error`: Server error

#### PATCH `/notifications/<notification_id>/users/<user_id>/read`
- **Description**: Mark a specific notification as read. Only the owner of the notification can mark it as read.
- **Path Parameters**:
  - `notification_id` (int): The notification ID
  - `user_id` (UUID): The user ID (for authorization check)
- **Response**: Updated `NotificationResponseSchema` object
- **Status Codes**:
  - `200 OK`: Notification marked as read successfully
  - `400 Bad Request`: Invalid parameters
  - `403 Forbidden`: User cannot modify another user's notification
  - `404 Not Found`: Notification not found or not authorized
  - `500 Internal Server Error`: Server error

#### DELETE `/notifications/<notification_id>/users/<user_id>`
- **Description**: Delete a specific notification. Only the owner of the notification can delete it.
- **Path Parameters**:
  - `notification_id` (int): The notification ID
  - `user_id` (UUID): The user ID (for authorization check)
- **Response**: Success message
- **Status Codes**:
  - `200 OK`: Notification deleted successfully
  - `400 Bad Request`: Invalid parameters
  - `403 Forbidden`: User cannot delete another user's notification
  - `404 Not Found`: Notification not found or not authorized
  - `500 Internal Server Error`: Server error

### Response Schema

```json
{
  "id": 1,
  "group_id": "123e4567-e89b-12d3-a456-426614174000",
  "group_name": "Family Group",
  "receiver": "456e7890-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-15T10:30:00Z",
  "template_code": "GROUP_USER_ADDED",
  "raw_data": {
    "requester_username": "john_doe",
    "requester_id": "789e0123-e89b-12d3-a456-426614174002"
  },
  "is_read": false,
  "title": "Chào mừng bạn gia nhập nhóm Family Group!",
  "content": "john_doe đã thêm bạn vào nhóm Family Group. Hãy bắt đầu lên thực đơn ngay nhé!"
}
```

## Consumed Kafka Topics

The service consumes messages from the following Kafka topics:

### OTP Topics (Email Delivery)
- `REGISTRATION_EVENTS_TOPIC`: User registration OTP emails
- `RESET_PASSWORD_EVENTS_TOPIC`: Password reset OTP emails
- `EMAIL_CHANGE_EVENTS_TOPIC`: Email change OTP emails

### System Topics
- `LOGOUT_EVENTS_TOPIC`: User logout events (disconnects user's WebSocket connections)

### Notification Topic (Event-Based Routing)
- `NOTIFICATION_TOPIC`: Unified topic for all in-app notifications, routed by `event_type`:
  - `group_user_added`: User added to a group
  - `group_user_removed`: User removed from a group
  - `group_user_left`: User left a group
  - `group_head_chef_updated`: Head chef role updated
  - `food_expiring_soon`: Food items expiring soon
  - `food_expired`: Food items expired
  - `plan_assigned`: Meal plan assigned to user
  - `plan_reported`: Meal plan reported
  - `plan_expired`: Meal plan expired
  - `daily_meal`: Daily meal notifications

### Message Format for NOTIFICATION_TOPIC

```json
{
  "event_type": "group_user_added",
  "group_id": "123e4567-e89b-12d3-a456-426614174000",
  "receivers": ["456e7890-e89b-12d3-a456-426614174001"],
  "receiver_is_head_chef": false,
  "data": {
    "group_name": "Family Group",
    "requester_username": "john_doe",
    "requester_id": "789e0123-e89b-12d3-a456-426614174002"
  }
}
```

## Database Schema

### Notifications Table

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    group_id UUID NOT NULL,
    group_name VARCHAR(255) NOT NULL,
    receiver UUID NOT NULL,
    created_at TIMESTAMP NOT NULL,
    template_code VARCHAR(100) NOT NULL,
    raw_data JSONB,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL
);

CREATE INDEX ix_notifications_group_id ON notifications(group_id);
CREATE INDEX ix_notifications_receiver ON notifications(receiver);
CREATE INDEX ix_notifications_is_read ON notifications(is_read);
```

### Fields Description

- `id`: Auto-incrementing integer primary key
- `group_id`: UUID of the group associated with the notification
- `group_name`: Name of the group
- `receiver`: UUID of the user receiving the notification
- `created_at`: Timestamp when the notification was created
- `template_code`: Code identifying the notification template (e.g., "GROUP_USER_ADDED")
- `raw_data`: JSONB field storing additional event-specific data
- `is_read`: Boolean flag indicating if the notification has been read
- `title`: Localized notification title
- `content`: Localized notification content/body

## Data Flow & Lifecycle

### 1. Client Connection (HTTP Upgrade to WSS)

1.  **Client Request:** The client initiates a connection by sending an HTTP `GET` request to the WebSocket endpoint (e.g., `wss://<gateway-host>/ws/v2/notification-service/notifications/users/<user_id>`).
2.  **Kong Gateway:** Kong receives the request. It performs authentication (e.g., validating the `Authorization: Bearer <JWT_TOKEN>` header) based on configured plugins (like `jwt` or `key-auth`). If successful, Kong forwards the request to the `notification-service`.
3.  **Notification Service:**
    *   The `ws_bp.py` endpoint (`ws_user_notifications`) receives the request.
    *   It performs authentication and authorization checks (e.g., verifying the requesting user ID matches the `user_id` in the path).
    *   If authorized, it calls `websocket_manager.connect_to_user(user_id, ws)`.
    *   The `WebSocketManager` stores the WebSocket connection object (`ws`) in its internal dictionary (`user_connections`) using the `user_id` as the key.
    *   The HTTP connection is upgraded to a persistent WSS connection.

### 2. Event Occurrence & Kafka Publishing

1.  **Action in Service:** An action occurs in another service (e.g., `user-service`, `food-service`, `plan-service`).
2.  **Publish to Kafka:** The service publishes a structured message to the appropriate Kafka topic (e.g., `NOTIFICATION_TOPIC` with `event_type`).

### 3. Notification Service Consumption & Dispatch

1.  **Kafka Consumer:** The `notification_consumer.py` in `notification-service` continuously polls the subscribed Kafka topics.
2.  **Message Received:** A message is received from a topic.
3.  **Handler Dispatch:** 
    - For OTP topics and `LOGOUT_EVENTS_TOPIC`, the consumer routes directly to the corresponding handler.
    - For `NOTIFICATION_TOPIC`, the consumer extracts the `event_type` and routes to the appropriate handler (e.g., `AddUserGroupHandler`, `FoodExpiringSoonHandler`).
4.  **Message Processing:** The handler:
    - Validates the message structure and content
    - Determines the receivers (if not provided in the message)
    - Creates notification records in the database
    - Generates localized title and content using templates
    - Sends the notification via WebSocket to connected clients using `websocket_manager.send_to_user(user_id, message)`

### 4. Client Disconnection (Client Initiated)

1.  **Client Closes:** The client application closes the WebSocket connection.
2.  **Notification Service Receives Close Event:** The `async for message in ws:` loop in the endpoint function exits.
3.  **Manager Cleanup:** The `finally` block in the endpoint executes, calling `websocket_manager.disconnect_from_user(ws, user_id)`.
4.  **Connection Removed:** The `WebSocketManager` removes the specific WebSocket connection object from its internal dictionary. If the set of connections for a `user_id` becomes empty, the key is removed entirely.

### 5. Server Disconnection (Server Initiated)

1.  **Server Shutdown:** The `notification-service` application receives a shutdown signal (SIGTERM, SIGINT).
2.  **Sanic Shutdown Hooks:** Sanic triggers shutdown hooks.
3.  **Consumer Shutdown:** The Kafka consumer loop (`consume_notifications`) is gracefully stopped using the shutdown event.
4.  **Manager Cleanup:** The `WebSocketManager` closes all active connections gracefully, sending a close frame to each client.
5.  **Client Notified:** Clients receive a WebSocket close event, indicating the disconnection.

### 6. Connection Errors & Recovery

*   **Network Issues:** If the network connection between client and server (or server and Kong, or server and Kafka) is lost, the connection will eventually timeout or close.
*   **Manager Error Handling:** The `WebSocketManager`'s `send_to_user` method includes error handling. If sending a message to a specific WebSocket connection fails (e.g., due to a broken pipe), the manager removes that connection from its internal storage to prevent sending to stale connections.
*   **Kafka Consumer Errors:** The Kafka consumer (`aiokafka`) has built-in retry mechanisms and error handling. If it fails to consume messages temporarily, it will attempt to reconnect and resume from the last committed offset.
*   **Client Reconnection:** Best practice for clients is to implement a reconnection strategy (e.g., exponential backoff) to handle temporary disconnections and resume listening for notifications.

## Testing Real-time Notifications

This section describes how to test the real-time notification flow end-to-end, from a user action in another service triggering a Kafka event, to `notification-service` consuming it and sending a WebSocket message.

### Prerequisites

1.  **Running Services:** Ensure the following services are up and running:
    *   `kafka` (and `zookeeper`)
    *   `notification-service`
    *   `user-service` (or other services that publish events)
    *   `api-gateway` (Kong)
    *   `postgres` (database)
    *   `redis` (for token validation)
2.  **User Accounts & Group:** You need at least two user accounts and one group created. You can use the `user-service` API (via Kong) to register, login, and create/manage groups.
    *   Example Users: `user_A` (UUID: `USER_A_ID`), `user_B` (UUID: `USER_B_ID`)
    *   Example Group: `Family_Group` (UUID: `GROUP_ID`)
3.  **Tools:** A WebSocket client (like Postman's WebSocket feature) to connect to the notification endpoints.

### Test Scenarios

#### Scenario 1: User Added to Group (`group_user_added`)

1.  **Setup WebSocket Connections:**
    *   **Client 1 (User B):** Connect to `ws://localhost:8000/ws/v2/notification-service/notifications/users/USER_B_ID`. Include a valid `Authorization: Bearer <JWT_TOKEN_USER_B>` header.
2.  **Trigger the Event:**
    *   Use the `user-service` API via Kong to add `user_B` to `Family_Group`.
    *   **Endpoint:** `POST http://localhost:8000/api/v1/user-service/api/v1/user-service/groups/GROUP_ID/members`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_A>` (or another group admin/head chef)
    *   **Body (JSON):**
        ```json
        {
          "user_identifier": "user_b_email@example.com"
        }
        ```
3.  **Observe Notifications:**
    *   **Client 1:** Should receive a WebSocket message with notification details
    *   **Database:** A notification record should be created in the `notifications` table
    *   **REST API:** `GET /api/v2/notification-service/notifications/users/USER_B_ID` should return the new notification

#### Scenario 2: User Removed from Group (`group_user_removed`)

1.  **Setup WebSocket Connections:**
    *   **Client 1 (User B):** Connect to `ws://localhost:8000/ws/v2/notification-service/notifications/users/USER_B_ID`. Include a valid `Authorization: Bearer <JWT_TOKEN_USER_B>` header.
2.  **Trigger the Event:**
    *   Use the `user-service` API via Kong to remove `user_B` from `Family_Group`.
    *   **Endpoint:** `DELETE http://localhost:8000/api/v1/user-service/api/v1/user-service/groups/GROUP_ID/members/USER_B_ID`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_A>` (or another group admin/head chef)
3.  **Observe Notifications:**
    *   **Client 1:** Should receive a WebSocket message
    *   **Database:** A notification record should be created
    *   **REST API:** The notification should be retrievable via the REST API

#### Scenario 3: User Leaves Group (`group_user_left`)

1.  **Setup WebSocket Connections:**
    *   Connect a client for `user_A` (or any other receiver) to the user notifications endpoint.
2.  **Trigger the Event:**
    *   Use the `user-service` API via Kong for `user_B` to leave the `Family_Group`.
    *   **Endpoint:** `DELETE http://localhost:8000/api/v1/user-service/api/v1/user-service/groups/GROUP_ID/members/me`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_B>`
3.  **Observe Notifications:**
    *   **Client:** Should receive a WebSocket message
    *   **Database:** Notification records should be created for other group members

#### Scenario 4: Head Chef Role Updated (`group_head_chef_updated`)

1.  **Setup WebSocket Connections:**
    *   Connect clients for the expected receivers to the user notifications endpoint.
2.  **Trigger the Event:**
    *   Use the `user-service` API via Kong to transfer the Head Chef role (e.g., from `user_A` to `user_B`).
    *   **Endpoint:** `PATCH http://localhost:8000/api/v1/user-service/api/v1/user-service/groups/GROUP_ID/head-chef`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_A>` (current head chef or admin)
    *   **Body (JSON):**
        ```json
        {
          "new_head_chef_user_id": "USER_B_ID"
        }
        ```
3.  **Observe Notifications:**
    *   **Client:** Should receive WebSocket messages for relevant users
    *   **Database:** Notification records should be created

#### Scenario 5: User Account Logout (`LOGOUT_EVENTS_TOPIC`)

1.  **Setup WebSocket Connections:**
    *   **Client 1 (User A):** Connect to `ws://localhost:8000/ws/v2/notification-service/notifications/users/USER_A_ID` with `user_A`'s token.
    *   **Client 2 (User B):** Connect to `ws://localhost:8000/ws/v2/notification-service/notifications/users/USER_B_ID` with `user_B`'s token.
2.  **Trigger the Event:**
    *   Use the `user-service` API via Kong to logout `user_A`.
    *   **Endpoint:** `POST http://localhost:8000/api/v1/user-service/api/v1/user-service/auth/logout`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_A>`
3.  **Observe Disconnection:**
    *   **Client 1:** Should receive a WebSocket close event, indicating the connection has been terminated.
    *   **Client 2:** Should remain connected and unaffected by `user_A`'s logout.

#### Scenario 6: Food Expiring Soon (`food_expiring_soon`)

1.  **Setup WebSocket Connections:**
    *   Connect clients for users who should receive food expiration notifications.
2.  **Trigger the Event:**
    *   The `food-service` publishes a message to `NOTIFICATION_TOPIC` with `event_type: "food_expiring_soon"`.
3.  **Observe Notifications:**
    *   **Client:** Should receive WebSocket messages with food expiration warnings
    *   **Database:** Notification records should be created

#### Scenario 7: REST API - Retrieve Notifications

1.  **Get User Notifications:**
    *   **Endpoint:** `GET http://localhost:8000/api/v2/notification-service/notifications/users/USER_B_ID`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_B>`
    *   **Response:** List of all notifications for the user

2.  **Mark Notification as Read:**
    *   **Endpoint:** `PATCH http://localhost:8000/api/v2/notification-service/notifications/1/users/USER_B_ID/read`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_B>`
    *   **Response:** Updated notification with `is_read: true`

3.  **Delete Notification:**
    *   **Endpoint:** `DELETE http://localhost:8000/api/v2/notification-service/notifications/1/users/USER_B_ID`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_B>`
    *   **Response:** Success message

### Notes

*   Ensure JWT tokens used for WebSocket connections are valid and belong to the user whose channel they are trying to access.
*   The exact structure of the received WebSocket message might vary slightly based on the `notification-service` implementation details.
*   The `LOGOUT_EVENTS_TOPIC` is consumed, but instead of sending a notification, it triggers the disconnection of all WebSocket connections for the logged-out user.
*   All notifications are persisted in the database, allowing users to retrieve their notification history via the REST API.
*   Notifications support localization with Vietnamese titles and content by default.

## Notification Types

The service supports the following notification types (identified by `template_code`):

### Group Management
- `GROUP_USER_ADDED`: User added to a group
- `GROUP_USER_REMOVED`: User removed from a group
- `GROUP_USER_LEFT`: User left a group
- `GROUP_HEAD_CHEF_UPDATED`: Head chef role updated

### Food Management
- `FOOD_EXPIRING_SOON`: Food items expiring soon
- `FOOD_EXPIRED`: Food items expired

### Meal Plan Management
- `PLAN_ASSIGNED`: Meal plan assigned to user
- `PLAN_REPORTED`: Meal plan reported
- `PLAN_EXPIRED`: Meal plan expired
- `DAILY_MEAL`: Daily meal notifications

### OTP Delivery (Email)
- OTP emails are sent for registration, password reset, and email change (not stored as in-app notifications)

## Development

### Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Run the service
python run.py
```

### Database Migrations

The service uses Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Environment Variables

Required environment variables (configured in `app/config.py`):
- Database connection settings
- Kafka broker settings
- Redis connection settings
- Email service settings (SMTP)
- JWT validation settings

## Architecture Notes

- **WebSocket Manager**: Maintains a dictionary of active connections per user, allowing multiple connections per user
- **Handler Pattern**: Each event type has a dedicated handler class that extends `BaseMessageHandler`
- **Database Persistence**: All notifications are stored in PostgreSQL for historical access
- **Real-time Delivery**: Active WebSocket connections receive notifications immediately
- **Email Service**: Separate service for sending OTP emails via SMTP
- **Token Validation**: Uses Redis to validate JWT token state and check blocklist
