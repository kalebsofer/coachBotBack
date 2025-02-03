import os
from logging.config import fileConfig
import time

from alembic import context
from sqlalchemy import engine_from_config, pool

from db.core.models import Base
from db.core.database import DATABASE_URL, get_sync_url

# this is the Alembic Config object
config = context.config

# Use sync URL for migrations
sync_url = get_sync_url(DATABASE_URL)
config.set_main_option("sqlalchemy.url", sync_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

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

def run_migrations_online() -> None:
    # Get URL from environment or config
    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    
    # Ensure we're using the correct host
    if "localhost" in url:
        url = url.replace("localhost", "postgres")
    
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
