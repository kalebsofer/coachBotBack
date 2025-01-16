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

COPY src/api/pyproject.toml src/api/poetry.lock ./
RUN poetry install --no-root

COPY src/api/ ./
COPY src/db/core ./db/core

ENV PATH="/usr/local/bin:/root/.local/bin:$PATH"

CMD ["poetry", "run", "uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000"]
