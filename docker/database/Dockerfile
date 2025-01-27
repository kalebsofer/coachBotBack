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

# Copy source code
COPY src/db/ ./

# Install dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

FROM postgres:16

ENV POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=coach_bot

COPY --from=builder /app/db/migrations /app/db/migrations
COPY --from=builder /app/db/core /app/db/core

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}

EXPOSE 5432