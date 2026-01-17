import sys
from app import create_app
from app.config import Config

app = create_app(Config)

def run():
    """Checks configuration and runs the application."""
    try:
        app.run(**app.config["RUN_SETTING"])
    except KeyboardInterrupt:
        pass
    except (BrokenPipeError, EOFError):
        # These errors can occur during shutdown with multiprocessing
        pass
    except (KeyError, OSError) as error:
        sys.exit(1)
    except Exception as error:
        sys.exit(1)


if __name__ == '__main__':
    run()
