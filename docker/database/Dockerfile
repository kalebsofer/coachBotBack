# Start with Python 3.12
FROM python:3.12-slim as python_base

# Now get PostgreSQL
FROM postgres:16

# Copy Python from python_base
COPY --from=python_base /usr/local/bin/python* /usr/local/bin/
COPY --from=python_base /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=python_base /usr/local/include/python3.12 /usr/local/include/python3.12
COPY --from=python_base /usr/local/lib/libpython3.12.so* /usr/local/lib/

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3.12 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages
RUN pip install psycopg2-binary alembic sqlalchemy python-dotenv asyncpg

# Copy initialization scripts
COPY src/db/migrations/scripts/init-db.sh /docker-entrypoint-initdb.d/
COPY src/db/migrations /app/db/migrations
COPY src/db/core /app/db/core
COPY src/db/alembic.ini /app/db/alembic.ini

ENV PYTHONPATH=/app

COPY src/db/config/postgresql.conf /etc/postgresql/postgresql.conf
COPY src/db/config/pg_hba.conf /etc/postgresql/pg_hba.conf

RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

ENV POSTGRES_CONFIG_FILE=/etc/postgresql/postgresql.conf \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=coach_bot

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}

EXPOSE 5432