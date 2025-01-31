# Database Service

The database service manages data persistence and access for the Coach Bot system using PostgreSQL, SQLAlchemy, and Alembic.

## Core Components

### Models (`core/models.py`)
- SQLAlchemy ORM models defining database schema
- Uses UUID primary keys for distributed safety
- Implements common mixins for timestamps and IDs
- Handles relationships between entities (User, Chat, Message, Log)

### Database Connection (`core/database.py`)
- Manages async database connections using SQLAlchemy 2.0
- Implements connection pooling for performance
- Provides session management and dependency injection
- Uses asyncpg for better async performance

### CRUD Operations (`core/crud.py`)
CRUD (Create, Read, Update, Delete) operations provide:
- Clean interface for database interactions
- Type-safe data access through generics
- Consistent error handling
- Business logic separation
- Reusable base operations
- Model-specific query methods

### Schemas (`core/schemas.py`)
- Pydantic models for data validation
- Separate schemas for creation and reading
- Type conversion and validation
- API request/response models
- SQLAlchemy model serialization

### Migrations (`migrations/`)
- Alembic for database schema version control
- Automatic migration generation
- Safe database updates
- Rollback capability
- Migration history tracking

## Stack

### PostgreSQL
- Robust relational database
- Strong UUID support
- JSONB for flexible storage

### SQLAlchemy
- Powerful ORM
- Type hints and async support
- Complex query capabilities
- Connection pooling
- Transaction management

### Alembic
- Database migration tool
- Works with SQLAlchemy
- Supports both auto and manual migrations
- Dependency resolution
- Branch management

### Pydantic
- Data validation using Python type annotations
- Automatic serialization/deserialization
- Integration with FastAPI
- Custom validators
- Schema documentation

## Development

### Prerequisites
- Python 3.12+
- Poetry for dependency management
- PostgreSQL 16+
- Docker and Docker Compose

### Environment Setup
```bash
# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Database Operations
```bash
# Create migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

### Docker
```bash
# Start database
docker-compose up -d postgres

# View logs
docker-compose logs -f postgres
```

## Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
