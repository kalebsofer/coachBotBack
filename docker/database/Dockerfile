FROM python:3.12-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.7.1 \
    PATH="/opt/poetry/bin:$PATH" \
    POETRY_INSTALL_OPTS="--no-interaction --no-ansi --no-dev"

FROM python-base as builder

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry - properly add to PATH
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./
COPY src/db ./db/

RUN poetry install --only main --no-root

FROM postgres:16

COPY --from=python-base /usr/local /usr/local
COPY --from=builder /app /app

WORKDIR /app

COPY src/db/init-db.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

ENV POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=coach_bot \
    PYTHONPATH=/app

HEALTHCHECK --interval=5s --timeout=5s --retries=3 \
    CMD pg_isready -U postgres || exit 1

EXPOSE 5432