# User Service API Documentation

This document provides an overview of the User Service API, including setup instructions, available endpoints for frontend developers.

## Overview
The User Service handles user authentication, authorization, user profiles, and family group management. It uses JWT tokens for authentication and provides RESTful API endpoints for managing user-related data.

### Authentication
All API requests (except authentication endpoints) require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

To obtain a JWT token, call the `/auth/login` endpoint with valid credentials.

### Base URL
```
http://localhost:8000/api/v1/user-service
```

### API Endpoints

#### Authentication
- `POST /auth/login` - Authenticate user and get JWT token
- `POST /auth/register` - Register a new user
- `POST /auth/logout` - Logout user
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset user password
- `POST /auth/otp/send` - Send OTP request for register or reset password
- `POST /auth/otp/verify` - Verify OTP

#### User Profile
- `GET /users/me` - Get current user information
- `POST /users/me/change-password` - Change user password
- `POST /users/me/email/request-change` - Request email change
- `POST /users/me/email/confirm-change` - Confirm email change
- `GET /users/me/profile/identity` - Get user's identity profile
- `GET /users/me/profile/health` - Get user's health profile
- `GET /users/me/tags` - Get user's tags
- `POST /users/me/tags/delete` - Delete user's tags
- `GET /users/me/tags/category/{category}` - Get user's tags by category
- `GET /users/{user_id}` - Get specific user information
- `GET /users/search` - Search users by criteria

#### Family Groups
- `GET /groups` - List user's family groups
- `POST /groups` - Create a new family group
- `GET /groups/{group_id}` - Get details of a specific family group
- `PUT /groups/{group_id}` - Update a family group
- `DELETE /groups/{group_id}` - Delete a family group
- `GET /groups/{group_id}/members` - List members in a group
- `POST /groups/{group_id}/members` - Add member to group
- `DELETE /groups/{group_id}/members/{user_id}` - Remove member from group
- `DELETE /groups/{group_id}/members/me` - Leave group
- `PUT /groups/{group_id}/members/{user_id}/role` - Update member role in group
- `PATCH /groups/{group_id}/members/{user_id}` - Update member in group
- `GET /groups/{group_id}/members/{user_id}/identity-profile` - Get member's identity profile
- `GET /groups/{group_id}/members/{user_id}/health-profile` - Get member's health profile

#### User Management (Admin)
- `GET /users` - List all users (admin only)
- `PUT /users/{user_id}/role` - Update user role (admin only)
- `DELETE /users/{user_id}` - Delete user (admin only)

#### Group Management (Admin)
- `GET /admin/groups` - Admin list groups
- `GET /admin/groups/{group_id}` - Admin get specific group
- `GET /admin/groups/{group_id}/members` - Admin list group members
- `GET /admin/users` - Admin list users
- `GET /admin/users/{user_id}` - Admin get specific user

## Setup

### Prerequisites
- Pull latest update on remote repository and at the root directory.
- Docker Desktop (Docker Engine) is installed and running on your machine (for local development).
- Python3.11+ is installed on your machine (for local development).

### Setup Environment Variables

Create new .env file in the root, user-service, notification-service directory and copy the content of .env.example into the newly created .env file.
```bash
cp .env.example .env
cp user-service/.env.example user-service/.env
cp notification-service/.env.example notification-service/.env
```

### Run user-service venv 
```bash
cd user-service
python3 -m venv .venv/
source .venv/bin/activate
```

### Generate RSA Keys
```bash
# Generate and verify RSA key pairs for JWT authentication
python3 generate_rsa_keys.py
python3 verify_rsa_keys_pair.py
```

After the command is complete, check the .env file to ensure that JWT_RSA_PUBLIC_KEY exists.

### Running with Docker
```bash
# From the project root directory
# If you have made code changes, use --build to rebuild images
docker compose up -d --build user-service
# Otherwise, use without --build for faster startup
docker compose --profile user-service up -d
```

### Initialize Admin User (after containers are running)
```bash
# Create admin user with default credentials
docker exec -it user-service python /app/user-service/scripts/create_admin_user.py

# Or create admin user with custom parameters
docker exec -it user-service python /app/user-service/scripts/create_admin_user.py --username "myadmin" --email "admin@example.com" --password "MySecurePassword123"
```

### Seed Tag Master Data
```bash
docker exec -it user-service python /app/user-service/scripts/seed_tags.py
```

### Database Setup & Migration Strategy

This project uses Alembic to manage database schema changes and migrations. Alembic tracks all database structure modifications through versioned migration files, ensuring consistent schema across different environments.

#### Important Notice
If you experience any database-related errors or synchronization issues, follow the reset procedure below. 
This will clear all existing migration history and regenerate the schema from the current models.

#### Complete Database Reset Procedure
Execute the following commands in sequence to perform a clean database reset:
```bash
# Step 1: Remove all existing migration files
rm -rf user-service/alembic/versions/*

# Step 2: Recreate the versions directory
mkdir -p user-service/alembic/versions

# Step 3: Stop and remove all containers with volumes
docker compose --profile user-service down -v

# Step 4: Rebuild and start the user-service container
docker compose up -d --build user-service

# Step 5: Generate new migration file from current models
docker exec -it user-service alembic revision --autogenerate -m "latest database schema"

# Step 6: Apply migrations to database
docker exec -it user-service alembic upgrade head
```

## Testing

### API Documentation
- Swagger UI: `http://localhost:8000/api/v1/user-service/docs/swagger`
- OpenAPI JSON: `http://localhost:8000/api/v1/user-service/docs/openapi.json`

### Postman Collection
Import the OpenAPI JSON file into Postman to get a complete collection of API endpoints.

### Postman Test Script
Use this script to automatically save the JWT token from login responses:

```javascript
// 1. Parse JSON response
var jsonData = pm.response.json();

// 2. Check if token exists in data.access_token path
if (jsonData.data && jsonData.data.access_token) {
    // 3. Save to environment variable
    pm.environment.set("jwt_token", jsonData.data.access_token);

    // Log to console for verification
    console.log("SUCCESS: Token saved:", jsonData.data.access_token);
} else {
    console.error("ERROR: Token not found! Check JSON structure.");
}
```