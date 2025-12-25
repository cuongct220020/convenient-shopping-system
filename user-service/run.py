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

# Disable Sanic Ext OpenAPI generation to avoid conflict with our custom /docs route
app.config.OAS = False
app.config.OAS_AUTODOC = False

@app.get("/openapi.json")
async def get_openapi_json(request):
    """Serve the custom OpenAPI specification."""
    spec_path = Path(__file__).parent / "openapi.yml"
    async with aiofiles.open(spec_path, mode='r', encoding='utf-8') as f:
        content = await f.read()
        spec = yaml.safe_load(content)
    return response.json(spec)

@app.get("/docs")
async def get_docs(request):
    """Serve Swagger UI."""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>SwaggerUI</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js" crossorigin></script>
        <script>
            window.onload = () => {
                window.ui = SwaggerUIBundle({
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                });
            };
        </script>
    </body>
    </html>
    """
    return response.html(html)

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