import warnings
from pydantic import PydanticDeprecatedSince20

warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20, module="sanic_ext")

from sanic import Sanic
from sanic_ext import Extend
from sanic.response import json as sanic_json


def register_routes(sanic_app: Sanic):
    """Register routes for the Notification Service."""

    @sanic_app.route("/api/v2/notification-service/", methods=["GET"])
    async def root(request):
        """Root endpoint."""
        return sanic_json({
            "service": "notification-service",
            "status": "running",
            "message": "Notification Service is running"
        })

    @sanic_app.route("/api/v2/notification-service/health", methods=["GET"])
    async def health_check(request):
        """Health check endpoint."""
        return sanic_json({
            "status": "healthy",
            "service": "notification-service"
        })

    # Register API Blueprints
    from app.apis import api, ws_api
    sanic_app.blueprint(api)
    sanic_app.blueprint(ws_api)


def register_middleware(sanic_app: Sanic):
    """Register middleware for the Notification Service."""
    from app.hooks.request_authentication import auth_middleware
    from app.hooks.caching import inject_redis_client
    from app.hooks.database import open_db_session, close_db_session

    # Follow user-service pattern:
    # - open_db_session early so request handlers can use request.ctx.db_session
    # - inject_redis_client before auth_middleware so token validation can use Redis
    sanic_app.register_middleware(open_db_session, "request")
    sanic_app.register_middleware(close_db_session, "response")

    # Register inject_redis_client FIRST so auth_middleware can use it
    sanic_app.register_middleware(inject_redis_client, "request")
    sanic_app.register_middleware(auth_middleware, "request")


def register_listeners(sanic_app: Sanic):
    """Register lifecycle listeners for the Notification Service."""
    from app.hooks.message_broker import setup_kafka, close_kafka
    from app.hooks.caching import setup_redis, close_redis
    from app.hooks.database import setup_db, close_db
    from app.services.email_service import EmailService
    # from app.services.noti_service import notification_service
    from app.hooks.message_broker import start_consumer, stop_consumer

    # Database setup must be registered (learn from user-service)
    sanic_app.register_listener(setup_db, "before_server_start")
    sanic_app.register_listener(close_db, "before_server_stop")

    # Initialize email service with the app config
    @sanic_app.listener("before_server_start")
    async def init_services(app, loop):
        """Initialize services that require app context."""
        # Attach email service to app context passing only config
        app.ctx.email_service = EmailService(app.config)

    # Start Kafka Consumer
    sanic_app.register_listener(start_consumer, "after_server_start")

    # Register Redis hooks
    sanic_app.register_listener(setup_redis, "before_server_start")
    sanic_app.register_listener(close_redis, "before_server_stop")

    # Register Kafka hooks
    sanic_app.register_listener(setup_kafka, "before_server_start")
    sanic_app.register_listener(close_kafka, "after_server_stop")

    # Stop Kafka cosumer
    sanic_app.register_listener(stop_consumer, "before_server_stop")


def create_app(*config_cls) -> Sanic:
    """Application factory for the Notification Service."""
    sanic_app = Sanic(__name__)

    # Load configurations
    for config in config_cls:
        sanic_app.update_config(config)
        # Make DEBUG available (used by setup_db)
        if hasattr(config, "RUN_SETTING") and "debug" in config.RUN_SETTING:
            sanic_app.config.DEBUG = config.RUN_SETTING["debug"]

    # Register routes (required by Sanic - at least one route must exist)
    register_routes(sanic_app)

    # Register middleware
    register_middleware(sanic_app)

    # Register lifecycle listeners
    register_listeners(sanic_app)

    # Configure Sanic Extensions with OpenAPI settings from config
    Extend(sanic_app, oas=True)

    # Apply OAS configuration from config if available
    # Only apply configuration if config_cls is not empty
    if config_cls:
        config = config_cls[0]  # Use the first config for OAS settings
        if hasattr(config, 'OAS'):
            # Set the OAS info from config
            if 'info' in config.OAS:
                sanic_app.config.API_TITLE = config.OAS['info'].get('title', 'API')
                sanic_app.config.API_VERSION = config.OAS['info'].get('version', '1.0.0')
                sanic_app.config.API_DESCRIPTION = config.OAS['info'].get('description', '')

            # Set servers if defined in config
            if 'servers' in config.OAS:
                sanic_app.config.OAS_SERVERS = config.OAS['servers']

            # Set security if defined in config
            if 'security' in config.OAS:
                sanic_app.config.OAS_SECURITY = config.OAS['security']

        # Set the OAS URL prefix from config
        if hasattr(config, 'OAS_URL_PREFIX'):
            sanic_app.config.OAS_URL_PREFIX = config.OAS_URL_PREFIX

        # Set Swagger UI configuration if available
        if hasattr(config, 'SWAGGER_UI_CONFIGURATION'):
            sanic_app.config.SWAGGER_UI_CONFIGURATION = config.SWAGGER_UI_CONFIGURATION

    # Register shared error handlers
    from shopping_shared.sanic.error_handler import register_shared_error_handlers
    register_shared_error_handlers(sanic_app)

    return sanic_app