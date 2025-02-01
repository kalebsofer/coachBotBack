#!/bin/bash
set -e

# Wait for postgres to be ready
until pg_isready -U "$POSTGRES_USER"; do
    echo "Waiting for postgres..."
    sleep 2
done

echo "PostgreSQL started"

# Run migrations if POSTGRES_DB exists
if [ "$POSTGRES_DB" ]; then
    echo "Running migrations..."
    cd /app/db
    alembic upgrade head
fi 