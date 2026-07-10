# shared/shopping_shared/databases/database_manager.py
from contextlib import asynccontextmanager
from typing import TypeAlias, Any, AsyncGenerator

from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from shopping_shared.exceptions import DatabaseError
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Database Manager")

# Type alias for the session maker, following PascalCase convention
AsyncSessionMaker: TypeAlias = async_sessionmaker[AsyncSession]


class DatabaseManager:
    """
    Manages PostgreSQL connection, engine, and sessions for common usage across microservices.
    Designed to be flexible for various environments, including AWS RDS.
    """

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_maker: AsyncSessionMaker | None = None

    async def setup(
        self,
        database_uri: str,
        debug: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
    ) -> None:
        """
        Initializes the database engine and session maker.
        """
        if not database_uri:
            raise DatabaseError("Database URI is not provided. Cannot set up database.")

        self.engine = create_async_engine(
            database_uri,
            echo=debug,
            poolclass = AsyncAdaptedQueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping
        )

        self.session_maker = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

        logger.info(f"Database engine initialized: {database_uri.split('://')[0]}://****:****@{database_uri.split('@')[-1]}")

    async def create_tables(self, base: Any) -> None:
        """
        Creates all database tables defined in the models associated with the provided Base.
        Each service will pass its own declarative_base (e.g., from app.models.base) here.
        """
        if not self.engine:
            raise DatabaseError("Database engine not initialized. Call setup() first.")
        if not hasattr(base, 'metadata') or not hasattr(base.metadata, 'create_all'):
            raise DatabaseError("Invalid Base object provided. It must have a .metadata.create_all method.")

        logger.info("Initializing database tables...")
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)
        logger.info("Database tables initialized successfully.")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, Any]:
        """
        Provides a transactional session.
        Usage: async with database_manager.get_session() as session:
                   # perform operations with session
        """
        if not self.session_maker:
            raise DatabaseError("Database not initialized. Call setup() first.")

        session = self.session_maker()
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Session encountered an error, rolling back: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

    async def dispose(self) -> None:
        """Dispose of the database engine and close all connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database engine disposed.")


# A single, shared instance for the entire application
database_manager = DatabaseManager()
