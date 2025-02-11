# Database Service

The database service manages data persistence for the Coach Bot system using PostgreSQL and SQLAlchemy.

## Core Components

### Models (`core/models.py`)
- SQLAlchemy ORM models defining three main tables:
  - Users: Stores user information
  - Chats: Manages chat sessions
  - Messages: Stores chat messages
- Uses UUID primary keys for distributed safety
- Implements timestamps for tracking creation time

### Database Connection (`core/database.py`)
- Manages async database connections using SQLAlchemy 2.0
- Uses asyncpg for better async performance
- Provides session management and dependency injection
- Configurable through environment variables

### Schemas (`core/schemas.py`)
- Pydantic models for data validation
- Separate schemas for creation and reading
- Type conversion and validation
- API request/response models

### Migrations (`migrations/`)
- Alembic for database schema version control
- Automatic table creation on startup
- Safe database updates
- Rollback capability

## Stack

### PostgreSQL
- Version: 16
- Robust relational database
- Strong UUID support
- Timezone-aware timestamps

### SQLAlchemy
- Version: 2.0
- Async support with asyncpg
- Type hints and validation
- Connection pooling

### Alembic
- Database migration tool
- Works with SQLAlchemy
- Automatic migration application
- Version control for schema changes

## Configuration

### Environment Variables
Required variables in root `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/coach_bot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=coach_bot
```

### PostgreSQL Configuration
Basic configuration in `config/`:
- `postgresql.conf`: Database settings
- `pg_hba.conf`: Access control

## Development

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Docker and Docker Compose

### Database Operations
```bash
# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"
```

### Docker
```bash
# Start database
docker-compose up -d postgres

# View logs
docker-compose logs -f postgres
```

## Registering The PostgreSQL Server in pgAdmin

To manage your PostgreSQL databases using pgAdmin, follow these steps:

1. **Open pgAdmin:**  
   Launch pgAdmin in your browser. If you're using Docker, it is often available at a URL such as `http://localhost:5050`.

2. **Log In:**  
   Use the default credentials from your `.env` file:
   - **Email:** `PGADMIN_DEFAULT_EMAIL` (e.g., `test@test.com`)
   - **Password:** `PGADMIN_DEFAULT_PASSWORD` (e.g., `test`)

3. **Register a New Server:**  
   In the pgAdmin sidebar, right-click on "Servers" and select "Create" → "Server...".

4. **Configure the Server Registration:**  
   In the "Create - Server" dialog:
   - **General Tab:**  
     - **Name:** Provide a friendly name for the server (e.g., "Coach Bot Database").

   - **Connection Tab:**  
     - **Host name/address:** Use the host value from your `.env`, e.g., `POSTGRES_HOST` (typically `postgres` in a Docker network).
     - **Port:** Default PostgreSQL port is `5432`.
     - **Maintenance database:** Use the database name from `POSTGRES_DB` (e.g., `coach_bot`).
     - **Username:** Use `POSTGRES_USER` (e.g., `postgres`).
     - **Password:** Use `POSTGRES_PASSWORD` (e.g., `postgrespword`).

5. **Save and Connect:**  
   Click "Save" to register the new server. You should now see your PostgreSQL server listed in the pgAdmin UI and be able to browse databases, run queries, and manage schema changes.

These steps allow you to connect pgAdmin to the same PostgreSQL instance used by the Coach Bot system.
