FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY src/api/ /app/api/
COPY src/db/ /app/db/

WORKDIR /app/api

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

ENV PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

CMD ["poetry", "run", "uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000"]
