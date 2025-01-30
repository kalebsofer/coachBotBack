#!/bin/bash
set -ex  # Add -x for verbose logging

# Wait for database to be ready
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
    echo "Waiting for database to be ready..."
    sleep 2
done

cd /app/db

echo "Setting up environment..."
export PYTHONPATH=/app/src

echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "Files in current directory:"
ls -la

echo "Running migrations..."
alembic upgrade head

echo "Initializing database..."
python3 -m core.init_db

echo "Database initialization completed" 