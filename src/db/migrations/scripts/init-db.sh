#!/bin/bash
set -e

until pg_isready -U "$POSTGRES_USER"; do
    echo "Waiting for postgres..."
    sleep 2
done

echo "PostgreSQL started"

if [ "$POSTGRES_DB" ]; then
    echo "Running migrations..."
    cd /app/db
    alembic upgrade head
fi 