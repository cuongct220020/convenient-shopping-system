from shopping_shared.middleware.sanic_auth import create_auth_middleware


# Create the authentication middleware with specific configurations for notification service
auth_middleware = create_auth_middleware(
    ignore_paths={
        "/",
        "/favicon.ico",
        "/health",
        "/api/v2/notification-service",
        "/api/v2/notification-service/",
        "/api/v2/notification-service/health"
    },
    ignore_prefixes=[
        "/api/v2/notification-service/docs",
        "/api/v2/notification-service/openapi",
        "/docs",
        "/openapi"
    ]
)