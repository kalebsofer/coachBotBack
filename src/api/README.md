# API Service

The API service is a FastAPI application that handles real-time chat interactions between users and the AI coaching system.

## Core Functionality

### Endpoints

- `GET /` - Root endpoint, returns service status
- `GET /health` - Health check endpoint, monitors API, OpenAI, and Stream services
- `POST /generate-response` - Main endpoint for generating AI responses

### Features

- Real-time chat using Stream Chat
- AI responses powered by OpenAI's GPT-4
- CORS support for web and mobile clients

## Development

### Prerequisites

- Python 3.12+
- Poetry
- Docker

### Local Setup
```bash
poetry install
poetry run pytest
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

Required environment variables (see `.env.example` in root directory):

```
OPENAI_API_KEY=your_openai_api_key
STREAM_API_KEY=your_stream_api_key
STREAM_SECRET=your_stream_secret
```

## Container

```bash
Build and run from root dir: 

docker build -t coach-bot-api -f docker/api/Dockerfile .

docker run -d \
-p 8000:8000 \
--env-file .env \
--name coach-bot-api \
coach-bot-api
```


### Testing

Tests use mocked external services (OpenAI and Stream), see `tests/test_main.py`.

```bash
poetry run pytest
```


## API Documentation

Once running, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Integration

### Client Applications
- Web client (React): `http://localhost:3000`
- Mobile client (Expo):
  - Web: `http://localhost:19006`
  - Development: `exp://localhost:19000`

### External Services
- OpenAI GPT-4 for message generation
- Stream Chat for real-time messaging