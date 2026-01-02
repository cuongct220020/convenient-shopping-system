from sanic import Sanic
from sanic.response import json as sanic_json
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Initialize Notification Service Application")


def register_routes(sanic_app: Sanic):
    """Register routes for the Notification Service."""

    @sanic_app.route("/api/v1/notification-service/", methods=["GET"])
    async def root(request):
        """Root endpoint."""
        return sanic_json({
            "service": "notification-service",
            "status": "running",
            "message": "Notification Service is running"
        })

    @sanic_app.route("/api/v1/notification-service/health", methods=["GET"])
    async def health_check(request):
        """Health check endpoint."""
        return sanic_json({
            "status": "healthy",
            "service": "notification-service"
        })

    # Register API Blueprints
    from app.apis import api
    sanic_app.blueprint(api)


def register_middleware(sanic_app: Sanic):
    """Register middleware for the Notification Service."""
    from app.hooks.request_authentication import auth_middleware
    from app.hooks.caching import inject_redis_client
    # Register inject_redis_client FIRST so auth_middleware can use it
    sanic_app.register_middleware(inject_redis_client, "request")
    sanic_app.register_middleware(auth_middleware, "request")


def register_listeners(sanic_app: Sanic):
    """Register lifecycle listeners for the Notification Service."""
    from app.hooks.message_broker import setup_kafka, close_kafka
    from app.hooks.caching import setup_redis, close_redis
    # from app.hooks.database import setup_db, close_db
    from app.consumers.notification_consumer import consume_notifications, request_shutdown
    from app.services.email_service import EmailService
    # from app.services.noti_service import notification_service

    # # Database setup must be registered
    # sanic_app.register_listener(setup_db, "before_server_start")
    # sanic_app.register_listener(close_db, "before_server_stop")

    # Initialize email service with the app config
    @sanic_app.listener("before_server_start")
    async def init_services(app, loop):
        """Initialize services that require app context."""
        # Attach email service to app context passing only config
        app.ctx.email_service = EmailService(app.config)
        logger.info("Email Service attached to app.ctx")

        # # Initialize services that require Database Engine
        # @sanic_app.listener("after_server_start")
        # async def init_db_services(app, loop):
        #     # Inject the engine into the global notification service
        #     if hasattr(app.ctx, 'db_engine'):
        #         notification_service.set_engine(app.ctx.db_engine)
        #     else:
        #         logger.error("DB Engine not found in app.ctx during service init")

    @sanic_app.listener("after_server_start")
    async def start_consumer(app, loop):
        """Start Kafka consumer after server is fully started."""
        logger.info("Starting Kafka consumer background task...")
        app.add_task(consume_notifications(app))


    # Register Redis hooks
    sanic_app.register_listener(setup_redis, "before_server_start")
    sanic_app.register_listener(close_redis, "before_server_stop")


    sanic_app.register_listener(setup_kafka, "before_server_start")
    sanic_app.register_listener(close_kafka, "after_server_stop")

    @sanic_app.listener("before_server_stop")
    async def stop_consumer(app, loop):
        """Request graceful shutdown of Kafka consumer."""
        logger.info("Requesting consumer shutdown...")
        request_shutdown()


def create_app(*config_cls) -> Sanic:
    """Application factory for the Notification Service."""
    logger.info(f"Sanic application initialized with {', '.join([config.__name__ for config in config_cls])}")

    sanic_app = Sanic(__name__)

    # Load configurations
    for config in config_cls:
        sanic_app.update_config(config)

    # Register routes (required by Sanic - at least one route must exist)
    register_routes(sanic_app)

    # Register middleware
    register_middleware(sanic_app)

    # Register lifecycle listeners
    register_listeners(sanic_app)

    return sanic_app