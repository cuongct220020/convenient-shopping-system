import asyncio
from logging.config import fileConfig
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path to find shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Import models for 'autogenerate' support
from shopping_shared.databases.base_model import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=os.path.abspath(dotenv_path))

# Get DB connection info from environment variables
DB_DRIVER = os.getenv("POSTGRES_DB_DRIVER")
DB_USER = os.getenv('POSTGRES_DB_USER')
DB_PASSWORD = os.getenv('POSTGRES_DB_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB_NAME')

# Use localhost when running locally (not in container)
# Check if running in container environment
import socket
try:
    # Try to resolve the configured host
    socket.getaddrinfo(os.getenv('POSTGRES_DB_HOST', 'localhost'), int(os.getenv('POSTGRES_DB_PORT', 5432)))
    # If successful, use the configured host
    DB_HOST = os.getenv('POSTGRES_DB_HOST')
except socket.gaierror:
    # If resolution fails, fall back to localhost
    DB_HOST = 'localhost'

DB_PORT = os.getenv('POSTGRES_DB_PORT')

DATABASE_URI = f'{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = DATABASE_URI
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Override the sqlalchemy.url from the .ini file with the one from env vars
    config.set_main_option('sqlalchemy.url', DATABASE_URI)

    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())