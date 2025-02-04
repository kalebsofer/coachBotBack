#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
until pg_isready -U "$POSTGRES_USER"; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 5
done

# Wait a bit more to ensure PostgreSQL is fully ready to accept connections
sleep 5

echo "PostgreSQL started, creating database..."

# Add debug output
echo "Executing SQL with POSTGRES_DB=${POSTGRES_DB}"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    DO
    \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}') THEN
            CREATE DATABASE ${POSTGRES_DB};
        END IF;
    END
    \$\$;
EOSQL

echo "Database created or already exists"

cd /app/db
# Use local socket connection since we're inside the postgres container
export DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@/${POSTGRES_DB}"
echo "Using alembic.ini at: $(pwd)/alembic.ini"

# Add debug output for database URL
echo "Using DATABASE_URL: ${DATABASE_URL}"
echo "Running migrations from $(pwd)"
echo "Available migration files:"
ls -la migrations/versions/
echo "Database URL: $DATABASE_URL"
echo "Current directory contents:"
ls -la
echo "Migrations directory contents:"
ls -la migrations/

set -x  # Enable command tracing
alembic -c alembic.ini upgrade head
set +x

echo "Migrations completed successfully"

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'SELECT 1' || exit 1
echo "PostgreSQL is fully initialized and ready" 