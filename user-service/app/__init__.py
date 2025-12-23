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
    from app.hooks.request_context import after_request
    from app.hooks.response_time import add_start_time, add_spent_time
    from app.hooks.database import open_db_session, close_db_session
    from app.hooks.caching import inject_redis_client
    from app.hooks.request_auth import auth_middleware

    # IMPORTANT: The order of middleware can be important.
    # Middlewares that wrap the handler are executed like onion layers.

    # 1. (Outermost) Measures and logs response time
    sanic_app.register_middleware(add_start_time, attach_to='request')
    sanic_app.register_middleware(add_spent_time, attach_to='response')

    # 2. Manages DB session lifecycle (commit, rollback, close)
    # This should wrap the business logic to ensure transactions are handled correctly.
    sanic_app.register_middleware(open_db_session, attach_to='request')
    sanic_app.register_middleware(close_db_session, attach_to='response')

    # 3. Injects Redis client into the request context
    sanic_app.register_middleware(inject_redis_client, attach_to='request')

    # 4. Authentication middleware
    sanic_app.register_middleware(auth_middleware, attach_to='request')

    # 5. (Innermost) Generic post-request hook
    sanic_app.register_middleware(after_request, attach_to='response')


def create_app(*config_cls) -> Sanic:
    logger.info(f"Sanic application initialized with { ', '.join([config.__name__ for config in config_cls]) }")

    sanic_app = Sanic("User Service Application")

    for config in config_cls:
        sanic_app.update_config(config)

    register_listeners(sanic_app)
    register_views(sanic_app)
    register_hooks(sanic_app)
    
    # Register shared error handlers
    from shopping_shared.sanic.error_handler import register_shared_error_handlers
    register_shared_error_handlers(sanic_app)

    return sanic_app