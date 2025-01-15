#!/bin/bash
set -e

# Wait for database to be ready
until pg_isready; do
    echo "Waiting for database..."
    sleep 2
done

echo "Database is ready, running migrations..."

# Run migrations
cd /db
poetry run alembic upgrade head

echo "Running database initialization..."
# Run initialization script
poetry run python -m app.init_db

echo "Database initialization completed" 