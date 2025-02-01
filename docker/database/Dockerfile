FROM python:3.12-slim as builder

WORKDIR /app/db

COPY src/db/ ./

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

FROM postgres:16

COPY src/db/config/postgresql.conf /etc/postgresql/postgresql.conf
COPY src/db/config/pg_hba.conf /etc/postgresql/pg_hba.conf

ENV POSTGRES_CONFIG_FILE=/etc/postgresql/postgresql.conf \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=coach_bot \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

# Install Python 3.12 using the official Debian repository
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    wget \
    libbz2-dev \
    curl \
    libpq-dev && \
    update-ca-certificates && \
    curl -O https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz && \
    tar -xf Python-3.12.2.tgz && \
    cd Python-3.12.2 && \
    ./configure --enable-optimizations && \
    make -j $(nproc) && \
    make install && \
    cd .. && \
    rm -rf Python-3.12.2* && \
    python3.12 -m venv /opt/venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir -p /app/db
COPY --from=builder /app/db /app/db

WORKDIR /app/db
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

COPY src/db/migrations/scripts/init-db.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}

EXPOSE 5432