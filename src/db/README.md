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
