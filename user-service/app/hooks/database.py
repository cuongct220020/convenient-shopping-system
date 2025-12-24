# user-service/app/hooks/database.py
from sanic import Sanic, Request

from shopping_shared.databases.database_manager import database_manager as postgres_db
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.databases.base_model import Base

logger = get_logger("Database Middleware")

async def setup_db(app: Sanic):
    """
    This hook initializes the database connection and creates tables using the shared manager.
    It runs once before the server starts.
    """
    db_uri = app.config.POSTGRESQL.DATABASE_URI
    debug = app.config.get("DEBUG", False)
    await postgres_db.setup(database_uri=db_uri, debug=debug)

    # Auto-create tables if they do not exist (useful for local dev). In production, prefer Alembic.
    try:
        await postgres_db.create_tables(Base)
    except Exception as ex:
        logger.error("Failed to ensure DB tables exist: %s", ex)
        # Continue startup; explicit migrations may run separately


async def close_db(_app: Sanic):
    """
    This hook closes the database connection pool when the server stops.
    """
    await postgres_db.dispose()


async def open_db_session(request: Request):
    """
    Opens a new DB session context and attaches it and the session to the request.
    """
    # Lưu trữ context manager trên request
    request.ctx.db_session_cm = postgres_db.get_session()
    # Enter context manager và lưu trữ session
    request.ctx.db_session = await request.ctx.db_session_cm.__aenter__()


async def close_db_session(request: Request, response, exception: Exception | None = None):
    """
    Closes the DB session context, which handles commit or rollback.
    """
    if hasattr(request.ctx, "db_session_cm"):
        # --- SỬA LỖI Ở ĐÂY ---
        # Lấy kiểu, giá trị, và traceback một cách an toàn
        exc_type = type(exception) if exception else None
        exc_value = exception
        exc_tb = getattr(exception, '__traceback__', None) if exception else None

        # Truyền các giá trị chính xác vào __aexit__
        await request.ctx.db_session_cm.__aexit__(exc_type, exc_value, exc_tb)
        # --- KẾT THÚC SỬA LỖI ---

    return response