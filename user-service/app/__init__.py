# user-service/app/__init__.py

from sanic import Sanic
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Initialize User Service Application")


def register_listeners(sanic_app: Sanic):
    from app.hooks.database import setup_db, close_db
    from app.hooks.caching import setup_redis, close_redis
    from app.hooks.message_broker import setup_kafka, close_kafka
    from app.utils.jwt_utils import JWTHandler

    async def setup_jwt(app, loop):
        JWTHandler.initialize(app)
        logger.info("JWT Handler initialized.")

    sanic_app.register_listener(setup_jwt, "before_server_start")

    # Register database hooks
    sanic_app.register_listener(setup_db, "before_server_start")
    sanic_app.register_listener(close_db, "after_server_stop")

    # Register Redis hooks
    sanic_app.register_listener(setup_redis, "before_server_start")
    sanic_app.register_listener(close_redis, "after_server_stop")
    
    # Register Kafka hooks
    sanic_app.register_listener(setup_kafka, "before_server_start")
    sanic_app.register_listener(close_kafka, "after_server_stop")

def register_views(sanic_app: Sanic):
    from app.apis import api # Import the api Blueprint.groups

    # Register the main API blueprint groups with the /api/v1/user-service prefix
    sanic_app.blueprint(api, url_prefix="/api/v1/user-service")

def register_hooks(sanic_app: Sanic):
    from app.hooks import SecurityHeadersMiddleware, ResponseTimeMiddleware
    from app.hooks.database import open_db_session, close_db_session
    from app.hooks.caching import inject_redis_client
    from app.hooks.request_auth import auth_middleware

    # Initialize middleware instances
    response_time_middleware = ResponseTimeMiddleware(slow_request_threshold_ms=1000.0)  # 1 second threshold
    security_headers_middleware = SecurityHeadersMiddleware()

    # IMPORTANT: The order of middleware execution follows onion-layer model
    # Request middlewares execute from outer to inner (top to bottom)
    # Response middlewares execute from inner to outer (bottom to top)

    # 1. (Outermost) Track request start time for latency measurement
    sanic_app.register_middleware(response_time_middleware.before_request, attach_to='request')

    # 2. Manage DB session lifecycle (commit, rollback, close)
    # Wraps business logic to ensure transactions are handled correctly
    sanic_app.register_middleware(open_db_session, attach_to='request')
    sanic_app.register_middleware(close_db_session, attach_to='response')

    # 3. Inject Redis client into request context for caching operations
    sanic_app.register_middleware(inject_redis_client, attach_to='request')

    # 4. Extract and validate user authentication from Kong headers
    sanic_app.register_middleware(auth_middleware, attach_to='request')

    # 5. Add security headers to all responses
    sanic_app.register_middleware(security_headers_middleware.add_security_headers, attach_to='response')

    # 6. (Innermost) Log response time and structured metrics
    sanic_app.register_middleware(response_time_middleware.after_request, attach_to='response')


def create_app(*config_cls) -> Sanic:
    logger.info(f"Sanic application initialized with { ', '.join([config.__name__ for config in config_cls]) }")

    sanic_app = Sanic(__name__)

    for config in config_cls:
        sanic_app.update_config(config)

    register_listeners(sanic_app)
    register_views(sanic_app)
    register_hooks(sanic_app)
    
    # Register shared error handlers
    from shopping_shared.sanic.error_handler import register_shared_error_handlers
    register_shared_error_handlers(sanic_app)

    return sanic_app