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
    # Create the session using the database manager's context manager
    request.ctx.db_session_context = postgres_db.get_session()
    # Enter the context and store the session
    request.ctx.db_session = await request.ctx.db_session_context.__aenter__()


async def close_db_session(
        request: Request,
        response, exception: Exception | None = None
    ):
    """
    Closes the DB session context, which handles commit or rollback.
    """
    if hasattr(request.ctx, "db_session_context"):
        session_context = request.ctx.db_session_context

        # Determine if we should rollback.
        # Rollback if there is an unhandled exception OR if the response status indicates an error (4xx/5xx).
        is_error_response = response is not None and response.status >= 400
        should_rollback = exception is not None or is_error_response

        try:
            if should_rollback:
                # We need to trigger the rollback logic in the context manager.
                # If we don't have a real exception object (handled HTTP error), create a synthetic one.
                real_exc = exception or Exception(f"HTTP {response.status} Response - Forcing Rollback")
                
                exc_type = type(real_exc)
                exc_value = real_exc
                exc_tb = getattr(real_exc, '__traceback__', None)

                # __aexit__ with exception args triggers session.rollback() in get_session
                await session_context.__aexit__(exc_type, exc_value, exc_tb)
            else:
                # Success case (2xx, 3xx) -> Commit
                await session_context.__aexit__(None, None, None)

        except Exception as e:
            # The get_session context manager re-raises the exception after rolling back.
            # We catch and suppress it here because we are in the response middleware.
            # We want to return the original 'response' object (which might be a 400/409 error)
            # to the client, rather than letting an exception bubble up and cause a 500 Server Error.
            if should_rollback:
                logger.debug(f"Suppressed expected exception after rollback: {e}")
            else:
                logger.error(f"Unexpected error during DB commit/close: {e}")
            pass

    return response