FROM python:3.12-slim as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential && \
    pip install poetry && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY src/db/pyproject.toml src/db/poetry.lock ./
RUN poetry install --no-root
COPY src/db/ ./

FROM postgres:16

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY src/db/init-db.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

ENV POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=coach_bot \
    PATH="/usr/local/bin:/root/.local/bin:$PATH" \
    LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}

EXPOSE 5432