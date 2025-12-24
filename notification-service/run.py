import sys
from app import create_app
from app.config import Config
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Notification Service")

app = create_app(Config)

def main() -> None:
    """Checks configuration and runs the application."""
    # Warn if the default secret key is being used in a non-debug environment
    if not app.config.get('DEBUG'):
        logger.warning(
            'JWT_SECRET is using the insecure default value in a production environment. '
            'Please set a strong secret key in your environment variables.'
        )

    try:
        app.run(**app.config['RUN_SETTING'])
    except KeyboardInterrupt:
        logger.info("Application stopped by user.")
    except (BrokenPipeError, EOFError):
        # These errors can occur during shutdown with multiprocessing
        logger.info("Application shutdown complete.")
    except (KeyError, OSError) as error:
        logger.error(f"Configuration error: {error}")
        sys.exit(1)
    except Exception as error:
        logger.error(f"Unexpected error: {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
