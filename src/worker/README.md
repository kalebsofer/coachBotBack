# Worker Service

The worker service is responsible for processing chat messages asynchronously through RabbitMQ. It handles AI responses using OpenAI's GPT-4o-mini model and logs the responses into the database for later retrieval.

## Functionality

### Message Processing
- Consumes messages from the RabbitMQ queue
- Processes user messages using OpenAI's GPT-4o-mini model
- Logs AI-generated responses into the database
- Handles message acknowledgment and error recovery

### Components
- RabbitMQ Consumer: Listens for incoming chat messages
- OpenAI Integration: Generates AI responses using the GPT-4o-mini model
- Database Logging: Persists AI responses and audit logs in the database
- Error Handling: Manages failed messages with requeue capability

## Development

### Prerequisites
- Python 3.12+
- Poetry for dependency management
- RabbitMQ
- OpenAI API key

### Environment Setup
```bash
# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Running Locally
```bash
# Start the worker
poetry run python -m app.main
```

## Testing

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app tests/

# Run specific test file
poetry run pytest tests/test_main.py
```

### Test Structure
- `tests/test_main.py`: Tests for message processing and RabbitMQ integration
- Mock integrations for OpenAI
- Error handling and recovery scenarios

## Docker

### Building
```bash
docker build -t coach-bot-worker -f docker/worker/Dockerfile .
```

### Running in Docker
```bash
docker run -d \
  --name coach-bot-worker \
  --env-file .env \
  coach-bot-worker
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f worker
```

## Configuration

### Environment Variables
- `RABBITMQ_HOST`: RabbitMQ server hostname
- `RABBITMQ_PORT`: RabbitMQ server port (default: 5672)
- `RABBITMQ_USER`: RabbitMQ username
- `RABBITMQ_PASS`: RabbitMQ password
- `QUEUE_NAME`: RabbitMQ queue name
- `OPENAI_API_KEY`: OpenAI API key 