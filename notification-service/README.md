# Notification Service

## Overview

This service handles real-time notifications for the Convenient Shopping System. It consumes events from Kafka topics published by other services (e.g., `user-service`) and delivers notifications to clients via WebSocket connections.

## WebSocket Endpoints

The service exposes a single WebSocket endpoint (user-only). In a local development environment (via Kong Gateway), use:

*   **User Notifications:**
    *   URL: `ws://localhost:8000/ws/v2/notification-service/notifications/users/<user_id>`
    *   Usage: For receiving personal notifications for a specific user.

**Authentication:**
These endpoints are protected. You must provide a valid JWT token.
1.  **Header:** `Authorization: Bearer <YOUR_JWT_TOKEN>` (Recommended for generic clients)
2.  **Query Parameter:** Append `?jwt=<YOUR_JWT_TOKEN>` to the URL (Useful for browser/simple testing)

    *Example:* `ws://localhost:8000/ws/v2/notification-service/notifications/users/123e4567-e89b-12d3-a456-426614174000?jwt=eyJhbG...`

*Note: In production, these endpoints are accessed via WSS (secure WebSocket).*

## Consumed Kafka Topics

The service consumes messages from the following topics to trigger notifications:

*   `user_service.group.add_users`
*   `user_service.group.remove_users`
*   `user_service.group.leave_groups`
*   `user_service.group.update_headchef_role`
*   `user_service.user.logout_account` (Handled differently - disconnects user's WebSocket connections)

## Data Flow & Lifecycle

This section details the complete lifecycle of a WebSocket notification, from client connection to server disconnection.

### 1. Client Connection (HTTP Upgrade to WSS)

1.  **Client Request:** The client initiates a connection by sending an HTTP `GET` request to the WebSocket endpoint (e.g., `wss://<gateway-host>/ws/v2/notification-service/notifications/users/<user_id>`).
2.  **Kong Gateway:** Kong receives the request. It performs authentication (e.g., validating the `Authorization: Bearer <JWT_TOKEN>` header) based on configured plugins (like `jwt` or `key-auth`). If successful, Kong forwards the request to the `notification-service`.
3.  **Notification Service:**
    *   The `ws_bp.py` endpoint (`ws_user_notifications`) receives the request.
    *   It performs any additional application-level authorization checks (e.g., verifying the requesting user ID matches the `user_id` in the path).
    *   If authorized, it calls `websocket_manager.connect_to_user(user_id, ws)`.
    *   The `WebSocketManager` stores the WebSocket connection object (`ws`) in its internal dictionary (`user_connections`) using the `user_id` as the key.
    *   The HTTP connection is upgraded to a persistent WSS connection.

### 2. Event Occurrence & Kafka Publishing

1.  **Action in `user-service`:** An action occurs in `user-service` (e.g., a user is added to a group).
2.  **Publish to Kafka:** `user-service` publishes a structured message to the appropriate Kafka topic (e.g., `user_service.group.add_users`).

### 3. Notification Service Consumption & Dispatch

1.  **Kafka Consumer:** The `notification_consumer.py` in `notification-service` continuously polls the subscribed Kafka topics.
2.  **Message Received:** A message is received from a topic.
3.  **Handler Dispatch:** The consumer identifies the topic and routes the message to the corresponding `BaseMessageHandler` (e.g., `AddUserGroupHandler`).
4.  **Message Processing:** The handler validates the message structure and content.
5.  **WebSocket Dispatch:** The handler sends the prepared payload to each receiver via `websocket_manager.send_to_user(user_id, message)`.

### 4. Client Disconnection (Client Initiated)

1.  **Client Closes:** The client application closes the WebSocket connection.
2.  **Notification Service Receives Close Event:** The `async for message in ws:` loop in the endpoint function exits.
3.  **Manager Cleanup:** The `finally` block in the endpoint executes, calling `websocket_manager.disconnect_from_user(ws, user_id)`.
4.  **Connection Removed:** The `WebSocketManager` removes the specific WebSocket connection object from its internal dictionary. If the set of connections for a `user_id` becomes empty, the key is removed entirely.

### 5. Server Disconnection (Server Initiated)

1.  **Server Shutdown:** The `notification-service` application receives a shutdown signal (SIGTERM, SIGINT).
2.  **Sanic Shutdown Hooks:** Sanic triggers shutdown hooks if configured.
3.  **Consumer Shutdown:** The Kafka consumer loop (`consume_notifications`) should be gracefully stopped using an event (e.g., `asyncio.Event`).
4.  **Manager Cleanup:** The `WebSocketManager` should ideally have a shutdown method to close all active connections gracefully, sending a close frame to each client. This might involve iterating through `user_connections` and calling `ws.close()` on each.
5.  **Client Notified:** Clients receive a WebSocket close event, indicating the disconnection.

### 6. Connection Errors & Recovery

*   **Network Issues:** If the network connection between client and server (or server and Kong, or server and Kafka) is lost, the connection will eventually timeout or close.
*   **Manager Error Handling:** The `WebSocketManager`'s `send_to_user` method includes error handling. If sending a message to a specific WebSocket connection fails (e.g., due to a broken pipe), the manager removes that connection from its internal storage to prevent sending to stale connections.
*   **Kafka Consumer Errors:** The Kafka consumer (`aiokafka`) has built-in retry mechanisms and error handling. If it fails to consume messages temporarily, it will attempt to reconnect and resume from the last committed offset.
*   **Client Reconnection:** Best practice for clients is to implement a reconnection strategy (e.g., exponential backoff) to handle temporary disconnections and resume listening for notifications.

## Testing Real-time Notifications

This section describes how to test the real-time notification flow end-to-end, from a user action in `user-service` triggering a Kafka event, to `notification-service` consuming it and sending a WebSocket message.

### Prerequisites

1.  **Running Services:** Ensure the following services are up and running:
    *   `kafka` (and `zookeeper`)
    *   `notification-service`
    *   `user-service`
    *   `api-gateway` (Kong)
2.  **User Accounts & Group:** You need at least two user accounts and one group created. You can use the `user-service` API (via Kong) to register, login, and create/manage groups.
    *   Example Users: `user_A` (UUID: `USER_A_ID`), `user_B` (UUID: `USER_B_ID`)
    *   Example Group: `Family_Group` (UUID: `GROUP_ID`)
3.  **Tools:** A WebSocket client (like Postman's WebSocket feature) to connect to the notification endpoints.

### Test Scenarios

#### Scenario 1: User Added to Group (`ADD_USERS_GROUP_EVENTS_TOPIC`)

1.  **Setup WebSocket Connections:**
    *   **Client 1 (User B):** Connect to `ws://localhost:8000/ws/v2/notification-service/notifications/users/USER_B_ID`. Include a valid `Authorization: Bearer <JWT_TOKEN_USER_B>` header.
2.  **Trigger the Event:**
    *   Use the `user-service` API via Kong to add `user_B` to `Family_Group`.
    *   **Endpoint:** `POST http://localhost:8000/api/v1/user-service/api/v1/user-service/groups/GROUP_ID/members`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_A>` (or another group admin/head chef)
    *   **Body (JSON):**
        ```json
        {
          "user_identifier": "user_b_email@example.com" // or username
        }
        ```
3.  **Observe Notifications:**
    *   **Client 1:** Should receive a WebSocket message like:
        ```json
        {
          "event_type": "group_user_added",
          "data": {
            "requester_id": "USER_A_ID",
            "requester_username": "user_a_username",
            "group_id": "GROUP_ID",
            "group_name": "Family_Group",
            "user_to_add_id": "USER_B_ID",
            "user_to_add_identifier": "user_b_email@example.com",
            "timestamp": "2024-05-21T10:00:00Z"
          }
        }
        ```

#### Scenario 2: User Removed from Group (`REMOVE_USERS_GROUP_EVENTS_TOPIC`)

1.  **Setup WebSocket Connections:**
    *   **Client 1 (User B):** Connect to `ws://localhost:8000/ws/v2/notification-service/notifications/users/USER_B_ID`. Include a valid `Authorization: Bearer <JWT_TOKEN_USER_B>` header.
2.  **Trigger the Event:**
    *   Use the `user-service` API via Kong to remove `user_B` from `Family_Group`.
    *   **Endpoint:** `DELETE http://localhost:8000/api/v1/user-service/api/v1/user-service/groups/GROUP_ID/members/USER_B_ID`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_A>` (or another group admin/head chef)
3.  **Observe Notifications:**
    *   **Client 1:** Should receive a WebSocket message like:
        ```json
        {
          "event_type": "group_user_removed",
          "data": {
            "requester_id": "USER_A_ID",
            "requester_username": "user_a_username",
            "group_id": "GROUP_ID",
            "group_name": "Family_Group",
            "user_to_remove_id": "USER_B_ID",
            "user_to_remove_identifier": "user_b_email@example.com",
            "timestamp": "2024-05-21T10:05:00Z"
          }
        }
        ```

#### Scenario 3: User Leaves Group (`LEAVE_GROUP_EVENTS_TOPIC`)

1.  **Setup WebSocket Connections:**
    *   Connect a client for `user_A` (or any other receiver) to the user notifications endpoint.
2.  **Trigger the Event:**
    *   Use the `user-service` API via Kong for `user_B` to leave the `Family_Group`.
    *   **Endpoint:** `DELETE http://localhost:8000/api/v1/user-service/api/v1/user-service/groups/GROUP_ID/members/me`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_B>`
3.  **Observe Notifications:**
    *   **Client:** Should receive a WebSocket message like:
        ```json
        {
          "event_type": "group_user_left",
          "data": {
            "user_id": "USER_B_ID",
            "user_identifier": "user_b_email@example.com",
            "group_id": "GROUP_ID",
            "group_name": "Family_Group",
            "timestamp": "2024-05-21T10:10:00Z"
          }
        }
        ```

#### Scenario 4: Head Chef Role Updated (`UPDATE_HEADCHEF_ROLE_EVENTS_TOPIC`)

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
    *   **Client:** Should receive a WebSocket message like:
        ```json
        {
          "event_type": "group_head_chef_updated",
          "data": {
            "requester_id": "USER_A_ID",
            "requester_username": "user_a_username",
            "group_id": "GROUP_ID",
            "group_name": "Family_Group",
            "old_head_chef_id": "USER_A_ID",
            "old_head_chef_identifier": "user_a_email@example.com",
            "new_head_chef_id": "USER_B_ID",
            "new_head_chef_identifier": "user_b_email@example.com",
            "timestamp": "2024-05-21T10:15:00Z"
          }
        }
        ```

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

#### Scenario 6: Multiple Group Members Added Simultaneously

1.  **Setup WebSocket Connections:**
    *   **Client 1 (User B):** Connect to `ws://localhost:8000/ws/v2/notification-service/notifications/users/USER_B_ID` with `user_B`'s token.
    *   **Client 2 (User C):** Connect to `ws://localhost:8000/ws/v2/notification-service/notifications/users/USER_C_ID` with `user_C`'s token.
2.  **Trigger the Event:**
    *   Use the `user-service` API via Kong to add multiple users to the group simultaneously.
    *   **Endpoint:** `POST http://localhost:8000/api/v1/user-service/api/v1/user-service/groups/GROUP_ID/members`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_A>` (group admin/head chef)
    *   **Body (JSON):**
        ```json
        {
          "user_identifiers": ["user_b_email@example.com", "user_c_email@example.com"]
        }
        ```
3.  **Observe Notifications:**
    *   **Client 1 & 2:** Each should receive individual `group_user_added` notifications.

#### Scenario 7: Group Deletion (When Last Member Leaves)

1.  **Setup WebSocket Connections:**
    *   Connect clients for the expected receivers to the user notifications endpoint.
2.  **Trigger the Event:**
    *   Use the `user-service` API via Kong for the last member to leave the group.
    *   **Endpoint:** `DELETE http://localhost:8000/api/v1/user-service/api/v1/user-service/groups/GROUP_ID/members/me`
    *   **Headers:** `Authorization: Bearer <JWT_TOKEN_USER_A>` (last member)
3.  **Observe Notifications:**
    *   Clients should receive a `group_user_left` notification as applicable.

#### Scenario 8: Concurrent Notifications to Multiple Recipients

1.  **Setup WebSocket Connections:**
    *   **Client 1 (User A):** Connect to user notifications endpoint.
    *   **Client 2 (User B):** Connect to user notifications endpoint.
    *   **Client 3 (User C):** Connect to user notifications endpoint.
2.  **Trigger Multiple Events:**
    *   Simultaneously trigger multiple group events (add, remove, role update) using different API calls.
3.  **Observe Notifications:**
    *   Each client should receive only the notifications relevant to them.
    *   Individual clients should receive only their personal notifications.

### Notes

*   Ensure JWT tokens used for WebSocket connections are valid and belong to the user whose channel they are trying to access.
*   The exact structure of the received WebSocket message might vary slightly based on the `notification-service` implementation details.
*   The `user_service.user.logout_account` topic is consumed, but instead of sending a notification, it triggers the disconnection of all WebSocket connections for the logged-out user.


## Version 2: REST Endpoints & Database Storage Implementation Plan

This section outlines the detailed plan for implementing version 2 of the notification service, which includes REST endpoints and database storage for notifications.

### 1. Database Schema Design

#### Notification Table
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(100) NOT NULL, -- e.g., 'group_user_added', 'group_user_removed', etc.
    event_type VARCHAR(100), -- e.g., 'group_user_added', 'group_user_removed', etc.
    data JSONB, -- Store additional event-specific data
    is_read BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_read (is_read),
    INDEX idx_notification_type (notification_type)
);
```

#### Notification Preferences Table (Optional)
```sql
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    websocket_notifications BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Database Integration

#### Dependencies to Add
- `asyncpg` for PostgreSQL async operations
- `SQLAlchemy` or `Databases` for ORM/database abstraction
- `alembic` for database migrations

#### Database Models
Create Pydantic models and SQLAlchemy models for:
- `Notification`
- `NotificationPreferences` (optional)

#### Database Migration Scripts
- Create migration scripts for the new tables
- Include scripts for future schema changes

### 3. REST API Endpoints

#### Authentication
All endpoints require JWT authentication in the Authorization header:
```
Authorization: Bearer <JWT_TOKEN>
```

#### Endpoints Specification

**GET /api/v2/notifications**
- Description: Retrieve user's notifications with pagination and filtering
- Query Parameters:
  - `page` (int, default: 1): Page number for pagination
  - `size` (int, default: 20, max: 100): Number of notifications per page
  - `type` (string, optional): Filter by notification type (e.g., 'group_user_added')
  - `is_read` (boolean, optional): Filter by read status
  - `start_date` (ISO 8601 string, optional): Filter notifications from this date
  - `end_date` (ISO 8601 string, optional): Filter notifications until this date
- Response: Paginated list of notifications with metadata
- Status Codes: 200 (OK), 401 (Unauthorized)

**GET /api/v2/notifications/{notification_id}**
- Description: Retrieve a specific notification by ID
- Path Parameter: `notification_id` (UUID)
- Response: Single notification object
- Status Codes: 200 (OK), 401 (Unauthorized), 404 (Not Found)

**PUT /api/v2/notifications/{notification_id}/read**
- Description: Mark a specific notification as read
- Path Parameter: `notification_id` (UUID)
- Response: Updated notification object
- Status Codes: 200 (OK), 401 (Unauthorized), 404 (Not Found)

**PUT /api/v2/notifications/{notification_id}/unread**
- Description: Mark a specific notification as unread
- Path Parameter: `notification_id` (UUID)
- Response: Updated notification object
- Status Codes: 200 (OK), 401 (Unauthorized), 404 (Not Found)

**PUT /api/v2/notifications/mark-all-read**
- Description: Mark all user's notifications as read
- Request Body: Empty
- Response: Success message
- Status Codes: 200 (OK), 401 (Unauthorized)

**DELETE /api/v2/notifications/{notification_id}**
- Description: Delete a specific notification (soft delete - mark as archived)
- Path Parameter: `notification_id` (UUID)
- Response: Success message
- Status Codes: 200 (OK), 401 (Unauthorized), 404 (Not Found)

**DELETE /api/v2/notifications/clear-all**
- Description: Clear all user's notifications (soft delete - mark as archived)
- Request Body: Empty
- Response: Success message
- Status Codes: 200 (OK), 401 (Unauthorized)

**GET /api/v2/notifications/unread-count**
- Description: Get count of unread notifications for the user
- Response: JSON object with unread count
- Status Codes: 200 (OK), 401 (Unauthorized)

### 4. Integration with Kafka Consumer

#### Modified Message Handling
- When receiving Kafka messages, the consumer should:
  1. Process the message as before for WebSocket delivery
  2. Create a new notification record in the database
  3. Include the original event data in the `data` field as JSON

#### Notification Creation Logic
- Extract relevant information from Kafka message
- Map event types to notification types
- Store user-specific notifications based on the event
- For group events, create notifications for all relevant users in the group

### 5. Service Layer Implementation

#### Notification Service Class
Create a service class with methods for:
- Creating notifications from Kafka events
- Retrieving user notifications with pagination and filtering
- Updating notification read status
- Deleting/archiving notifications
- Getting unread notification counts

#### Database Repository Layer
Create repository classes for:
- CRUD operations on notifications
- Complex queries with filtering and pagination
- Batch operations (mark all as read, etc.)

### 6. API Blueprint Implementation

#### Route Handlers
Create Sanic route handlers for all REST endpoints:
- Validate input parameters
- Authenticate and authorize users
- Call appropriate service methods
- Return properly formatted responses
- Handle errors appropriately

#### Request/Response Models
Define Pydantic models for:
- Request validation (query parameters, request bodies)
- Response formatting
- Error responses

### 7. Security Considerations

#### Authorization
- Ensure users can only access their own notifications
- Validate JWT tokens properly
- Implement proper role-based access if needed

#### Input Validation
- Validate all input parameters
- Prevent SQL injection through proper ORM usage
- Validate UUID formats

#### Rate Limiting
- Implement rate limiting for notification endpoints
- Prevent abuse of notification APIs

### 8. Testing Strategy

#### Unit Tests
- Test database repository methods
- Test notification service logic
- Test API route handlers with mocked dependencies

#### Integration Tests
- Test complete API flows
- Test Kafka consumer integration with database
- Test WebSocket and REST API interactions

#### End-to-End Tests
- Test complete notification lifecycle
- Test both WebSocket and REST API functionality

### 9. Performance Considerations

#### Database Indexing
- Properly index frequently queried fields
- Optimize queries for pagination
- Consider partial indexes for boolean fields

#### Caching
- Cache frequently accessed data
- Consider Redis for notification counts
- Cache user preferences

#### Pagination
- Implement efficient pagination for large notification sets
- Use cursor-based pagination for better performance

### 10. Monitoring and Logging

#### Logging
- Log all notification operations
- Log Kafka consumer activities
- Log API access and errors

#### Metrics
- Track notification delivery rates
- Monitor API response times
- Monitor database query performance

### 11. Deployment Considerations

#### Environment Variables
- Database connection details
- Migration settings
- Performance tuning parameters

#### Health Checks
- Database connectivity check
- Kafka consumer status
- API endpoint health

#### Migration Strategy
- Plan for database schema migrations
- Consider data migration from existing systems
- Plan for zero-downtime deployments