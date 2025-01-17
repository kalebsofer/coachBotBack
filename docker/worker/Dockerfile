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

COPY src/worker/pyproject.toml src/worker/poetry.lock ./
RUN poetry install --no-root

COPY src/worker/ ./

ENV PATH="/usr/local/bin:/root/.local/bin:$PATH"

COPY <<EOF /entrypoint.sh
#!/bin/bash
python -m core.main
EOF

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"] 