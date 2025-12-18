from app import create_app
from config import Config, EmailConfig
from shared.shopping_shared.utils.logger_utils import get_logger

logger = get_logger(__name__)

# Create the Sanic app instance
app = create_app(Config, EmailConfig)

def main() -> None:
    """Checks configuration and runs the application."""
    try:
        app.run(**app.config['RUN_SETTING'])
    except (KeyError, OSError) as error:
        logger.error(f"Failed to start application: {error}", exc_info=True)
        raise error

if __name__ == '__main__':
    main()
