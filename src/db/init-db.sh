#!/bin/bash
set -e

# Wait for database to be ready
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
    echo "Waiting for database to be ready..."
    sleep 2
done

cd /app

# Run migrations
poetry run alembic upgrade head

# Initialize database with required data
poetry run python -m core.init_db

echo "Database initialization completed" 