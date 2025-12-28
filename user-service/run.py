# user-service/run.py
from sanic import response
from app import create_app
from shopping_shared.utils.logger_utils import get_logger
from app.config import Config

logger = get_logger("User Service Entrypoint")

# Create the Sanic app instance
app = create_app(Config)

# 1. Route Trang chủ (/): Hiển thị thông báo service đang chạy
@app.get("/")
async def root(request):
    return response.json({
        "service": "User Service",
        "status": "RUNNING",
        "version": "1.0.0",
        "message": "Welcome to Convenient Shopping System API"
    }, status=200)


def run():
    """Checks configuration and runs the application."""
    # Production Readiness Checks
    is_debug = app.config.get("RUN_SETTING", {}).get("debug", False)
    jwt_algo = app.config.get("JWT_ALGORITHM", "HS256")
    
    if not is_debug:
        logger.info("Checking production security configuration...")
        
        # 1. Ensure Asymmetric algorithm is used
        if not jwt_algo.startswith("RS"):
            logger.critical(
                f"INSECURE CONFIGURATION: JWT_ALGORITHM is set to '{jwt_algo}' in production. "
                "RS256 (Asymmetric) is required for Kong Gateway integration."
            )
            return

        # 2. Ensure Private Key is present (needed for signing)
        if not app.config.get("JWT_PRIVATE_KEY"):
            logger.critical(
                "MISSING PRIVATE KEY: RSA private key is required to sign JWT tokens in production. "
                "Check your JWT_PRIVATE_KEY_PATH environment variable."
            )
            return
            
        logger.info("Security configuration verified: RS256 with Private Key loaded.")

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