# user-service/run.py


import yaml
import aiofiles
from pathlib import Path
from sanic import response
from app import create_app
from shopping_shared.utils.logger_utils import get_logger
from app.config import Config

logger = get_logger("User Service Entrypoint")

# Create the Sanic app instance
app = create_app(Config)

# The line below is removed to allow sanic-ext to auto-generate the spec
# app.config.OAS_PATH_TO_SPEC = "openapi.yml"

# Configure OpenAPI Security Schemes
app.config.OAS_SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
    }
}

# Apply Security Scheme globally to all endpoints
app.config.OAS_SECURITY = [{"BearerAuth": []}]


# 1. Route Trang chủ (/): Hiển thị thông báo service đang chạy
@app.get("/")  # <--- 2. Sử dụng @app thay vì @sanic_app
async def root(request):
    return response.json({
        "service": "User Service",
        "status": "RUNNING",
        "version": "1.0.0",
        "message": "Welcome to Convenient Shopping System API"
    }, status=200)


# 2. Route Favicon (/favicon.ico): Trả về rỗng
@app.get("/favicon.ico")
async def favicon(request):
    return response.empty()


def run():
    """Checks configuration and runs the application."""
    # Warn if the default secret key is being used in a non-debug environment
    if not app.config.get('DEBUG') and app.config.get('JWT_SECRET') == None:
        logger.warning(
            'JWT_SECRET is using the insecure default value in a production environment. '
            'Please set a strong secret key in your environment variables.'
        )

    try:
        app.run(**app.config['RUN_SETTING'])
    except (KeyError, OSError) as error:
        raise error
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down gracefully...")
        # Sanic handles shutdown gracefully by default with its listeners
        logger.info("Application shutdown complete.")


if __name__ == '__main__':
    run()