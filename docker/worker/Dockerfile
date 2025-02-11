FROM python:3.12-slim

WORKDIR /app/worker

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY src/worker/pyproject.toml src/worker/poetry.lock ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

COPY src/worker/core ./core
COPY src/common/ /app/common/

ENV PYTHONPATH=/app

CMD ["poetry", "run", "python", "-m", "core.main"] 