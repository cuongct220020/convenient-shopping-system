from app import create_app
from shopping_shared.utils.logger_utils import get_logger
from config import Config

logger = get_logger(__name__)

# Create the Sanic app instance as a module-level constant
app = create_app(Config)

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

def main() -> None:
    """Checks configuration and runs the application."""
    # Warn if the default secret key is being used in a non-debug environment
    if not app.config.get('DEBUG') and app.config.get('JWT_SECRET') == '85c145a16bd6f6e1f3e104ca78c6a102':
        logger.warning(
            'JWT_SECRET is using the insecure default value in a production environment. '
            'Please set a strong secret key in your environment variables.'
        )

    try:
        app.run(**app.config['RUN_SETTING'])
    except (KeyError, OSError) as error:
        raise error

if __name__ == '__main__':
    main()