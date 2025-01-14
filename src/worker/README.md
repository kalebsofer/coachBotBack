# Worker Service

The worker service is responsible for processing chat messages asynchronously through RabbitMQ. It handles AI responses using OpenAI's GPT-4 and manages message delivery via Stream Chat.

## Functionality

### Message Processing
- Consumes messages from RabbitMQ queue
- Processes user messages using OpenAI's GPT-4
- Delivers AI responses through Stream Chat
- Handles message acknowledgment and error recovery

### Components
- RabbitMQ Consumer: Listens for incoming chat messages
- OpenAI Integration: Generates AI responses
- Stream Chat: Delivers messages to users
- Error Handling: Manages failed messages with requeue capability

## Development

### Prerequisites
- Python 3.12+
- Poetry for dependency management
- RabbitMQ
- OpenAI API key
- Stream Chat credentials

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
- Mock integrations for OpenAI and Stream Chat
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
- `STREAM_API_KEY`: Stream Chat API key
- `STREAM_SECRET`: Stream Chat API secret 