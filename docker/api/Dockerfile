FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app/src \
    PATH="/usr/local/bin:$PATH"

COPY src/api/pyproject.toml ./pyproject.toml
COPY src/api/poetry.lock ./poetry.lock

RUN poetry install --only main --no-root

COPY src/api/ ./src/api/
COPY src/db/ ./src/db/

CMD ["python", "-m", "uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
