FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY src/api/ /app/api/
COPY src/db/ /app/db/
COPY src/common/ /app/common/

WORKDIR /app/api

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Make sure the script is executable
RUN chmod +x wait-for-it.sh

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["poetry", "run", "uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
