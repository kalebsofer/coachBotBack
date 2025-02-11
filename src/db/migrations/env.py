import os
import time
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from common.db.models import Base
from db.core.database import DATABASE_URL, get_sync_url

config = context.config

sync_url = get_sync_url(DATABASE_URL)
config.set_main_option("sqlalchemy.url", sync_url)

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
    max_retries = 5
    retry_interval = 5

    for attempt in range(max_retries):
        try:
            url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

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
            break  # If successful, break the retry loop
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(
                f"Migration attempt {attempt + 1} failed, retrying in {retry_interval} seconds..."
            )
            time.sleep(retry_interval)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
