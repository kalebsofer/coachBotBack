# API Service

The API service handles HTTP requests, message processing, and integrations with OpenAI, Stream Chat, and the database.

## Core Components

### Main Application (`app/main.py`)
- FastAPI application setup and configuration
- Route handlers for:
  - Health checks and monitoring
  - Message processing and AI responses
  - Chat management
- Integrations with:
  - OpenAI for AI responses
  - Stream Chat for real-time messaging
  - Database for persistence
- Error handling and logging
- CORS and middleware configuration

### Database Utilities (`app/db.py`)
- Database session management
- Async session dependency for FastAPI
- Connection pooling and lifecycle management
- Integration with SQLAlchemy models
- Session cleanup and error handling

### API Utilities (`app/utils.py`)
- Health check functionality
- Route discovery and documentation
- Logging configuration
- Common helper functions
- API status monitoring

## Technology Stack

### FastAPI
- Modern, async web framework
- OpenAPI documentation
- Type hints and validation
- Dependency injection
- High performance

### OpenAI Integration
- GPT-4 model integration
- Async API calls
- Error handling
- Response processing

### Stream Chat
- Real-time messaging
- Channel management
- User authentication
- Message synchronization

## Development

### Prerequisites
- Python 3.12+
- Poetry for dependency management
- OpenAI API key
- Stream Chat credentials
- PostgreSQL database

### Environment Setup
```bash
# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Running the API
```bash
# Development
poetry run uvicorn app.main:app --reload

# Production
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker
```bash
# Build container
docker-compose build api

# Run service
docker-compose up -d api

# View logs
docker-compose logs -f api
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key
- `STREAM_API_KEY`: Stream Chat API key
- `STREAM_SECRET`: Stream Chat secret
- `ALLOWED_ORIGINS`: CORS allowed origins
- `DATABASE_URL`: PostgreSQL connection string

### API Routes
- `/`: Root endpoint, service status
- `/health`: Health check endpoint
- `/generate-response`: AI response generation
- `/api/v1/chat/message`: Message handling endpoint