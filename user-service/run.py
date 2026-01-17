# user-service/run.py
from sanic import response
from sanic_ext.extensions.openapi import openapi

from app import create_app
from app.config import Config

# Create the Sanic app instance
app = create_app(Config)

# 1. Route Trang chủ (/): Hiển thị thông báo service đang chạy
@app.get("/api/v1/user-service/health")
@openapi.tag("Home Page")
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
        # 1. Ensure Asymmetric algorithm is used
        if not jwt_algo.startswith("RS"):
            return

        # 2. Ensure Private Key is present (needed for signing)
        if not app.config.get("JWT_PRIVATE_KEY"):
            return

    # Run the application with proper signal handling
    try:
        app.run(**app.config['RUN_SETTING'])
    except KeyboardInterrupt:
        pass
    except RuntimeError as e:
        if "Event loop stopped before Future completed" in str(e):
            pass
        else:
            raise e


if __name__ == '__main__':
    run()