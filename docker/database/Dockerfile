FROM python:3.12-slim as builder

WORKDIR /app/db

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY src/db/ ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

FROM postgres:16

ENV POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=coach_bot \
    PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/

COPY --from=builder /app/db/migrations /app/db/migrations
COPY --from=builder /app/db/core /app/db/core
COPY src/db/init.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init.sh

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}

EXPOSE 5432