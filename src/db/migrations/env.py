import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from db.core.models import Base  # Import all models
from db.core.database import DATABASE_URL

# this is the Alembic Config object
config = context.config

# Set the database URL in the alembic config
config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("postgresql+asyncpg", "postgresql"))  # Use sync URL for migrations

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Use non-async engine for migrations
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = configuration["sqlalchemy.url"].replace("postgresql+asyncpg", "postgresql")
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        connectable = config.attributes.get("connection", None)
        if connectable is None:
            # Create our own engine if no connection was passed
            connectable = config.attributes.get("connection", None)
            if connectable is None:
                # Create our own engine if no connection was passed
                from sqlalchemy import create_engine
                connectable = create_engine(configuration["sqlalchemy.url"])

    with connectable.connect() as connection:
        do_run_migrations(connection)

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
