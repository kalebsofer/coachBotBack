FROM python:3.12-slim as builder

WORKDIR /app/db

# Copy only the db module
COPY src/db/ ./

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

FROM postgres:16

# Copy configuration files
COPY src/db/config/postgresql.conf /etc/postgresql/postgresql.conf
COPY src/db/config/pg_hba.conf /etc/postgresql/pg_hba.conf

# Set environment variable for config file location
ENV POSTGRES_CONFIG_FILE=/etc/postgresql/postgresql.conf

ENV POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=coach_bot \
    PYTHONPATH=/app

# Create directory structure
RUN mkdir -p /app/db

COPY --from=builder /usr/local/bin/python3 /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/lib/libpython3.12.so* /usr/local/lib/

# Copy db module to correct location
COPY --from=builder /app/db /app/db

COPY src/db/migrations/scripts/init-db.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

# Verify the structure
RUN ls -la /app/db && \
    python3 -c "import sys; print(sys.path)" && \
    python3 -c "from db.core.models import Base; print('Import test successful!')"

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}

EXPOSE 5432