#!/bin/bash
set -ex  # Add -x for verbose logging

# Wait for database to be ready
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
    echo "Waiting for database to be ready..."
    sleep 2
done

cd /app

# Run commands as postgres user
echo "Setting up environment..."
export PATH="/usr/local/bin:/usr/bin:$PATH"
export PYTHONPATH=/app/src
export HOME=/home/postgres

echo "Current user: $(whoami)"
echo "Postgres user exists: $(id postgres || echo 'no')"
echo "Python version: $(python3 --version)"
echo "Poetry version: $(poetry --version)"

# Run migrations and init as postgres user
echo "Running migrations..."
su postgres -c "poetry run alembic upgrade head"

echo "Initializing database..."
su postgres -c "poetry run python -m core.init_db"

echo "Database initialization completed" 