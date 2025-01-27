FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy entire source directories
COPY src/api/ /app/api/
COPY src/db/ /app/db/

WORKDIR /app/api

# Install dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

ENV PYTHONPATH=/app

CMD ["poetry", "run", "uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000"]
