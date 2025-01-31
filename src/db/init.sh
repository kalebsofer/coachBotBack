#!/bin/bash
set -ex  # Add -x for verbose logging

# Wait for postgres to be ready
until pg_isready -U "$POSTGRES_USER"; do
    echo "Waiting for postgres to be ready..."
    sleep 2
done

echo "Creating database if it doesn't exist..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    SELECT 'CREATE DATABASE $POSTGRES_DB'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB')\gexec
EOSQL

# Wait for the new database to be ready
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
    echo "Waiting for $POSTGRES_DB database to be ready..."
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
python3 -m alembic -c /app/db/alembic.ini upgrade head

echo "Initializing database..."
python3 -m core.init_db

echo "Database initialization completed" 