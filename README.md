# CoachBotBack

Backend service for CoachBot, built with FastAPI and Python.

## Project Structure

```
coachBotBack/
├── src/
│ └── /
│ ├─── api/
│ │     ├── __init__.py
│ │     └── main.py
│ └─── workers/
│ │     ├── __init__.py
│ │     └── main.py
├── tests/
├── docker/
│ ├── api/
│ │     ├── Dockerfile
│ ├── workers/
│ │     ├── Dockerfile
├── .env.example
├── .pre-commit-config.yaml
├── .gitignore
└── poetry.toml
```

## Local Dev

### Prerequisites

- Python 3.12+
- Poetry
- Git

### Initial Setup

1. Clone repository:

```bash
git clone <repository-url>
cd coachBotBack
```

2. Install Poetry if you haven't already:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Configure Poetry to create virtual environment in project directory:

```bash
poetry config virtualenvs.in-project true
```

4. Install dependencies:

```bash
poetry install
```

5. Set up pre-commit hooks:

```bash
poetry run pre-commit install
```

6. Copy the example environment file:

```bash
cp .env.example .env
```

### Running the Application

1. Activate the virtual environment:

```bash
poetry shell
```

2. Start the development server:

```bash
poetry run uvicorn .api.main:app --reload
```

The API will be available at `http://localhost:8000`

### Service Dependencies and Deployment

When rebuilding or deploying services, it's important to maintain the correct dependency order:

Dependencies Map:
1. Base Services (no dependencies):
   - postgres
   - rabbitmq
   - loki

2. Core Services:
   - api (depends on: postgres, rabbitmq)
   - worker (depends on: rabbitmq)
   - pgadmin (depends on: postgres)

3. Monitoring:
   - prometheus (depends on: api, worker)
   - grafana (depends on: prometheus, loki)

4. Frontend:
   - frontend (depends on: api)

Common Rebuild Commands:
```bash
# Rebuild and restart API and its dependents
docker compose up -d --force-recreate api frontend prometheus

# Rebuild worker and its dependents
docker compose up -d --force-recreate worker prometheus

# Rebuild monitoring stack
docker compose up -d --force-recreate prometheus grafana

# Rebuild postgres and its dependents
docker compose up -d --force-recreate postgres api pgadmin
```

### Running Tests

```bash
poetry run pytest
```

## Contributing

1. Prior to commit, format your code:

```bash
poetry run black .
poetry run isort .
```

2. Commit your changes:

```bash
git add .
git commit -m "Your descriptive commit message"
```

The pre-commit hooks will automatically check and format your code before committing.

3. Push your changes and create a pull request:

```bash
git push origin feature/your-feature-name
```

## Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- flake8 for code linting

These are automatically run via pre-commit hooks.

## Environment Variables

Create a `.env` file in the root directory, see `.env.example` for reference.
