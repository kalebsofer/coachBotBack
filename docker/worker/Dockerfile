FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy entire worker directory
COPY src/worker/ /app/worker/

WORKDIR /app/worker

# Install dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

ENV PYTHONPATH=/app

CMD ["python", "-m", "core.main"] 