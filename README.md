# MetaGuard

MetaGuard is a Django-based data governance platform for dataset intake review. It helps teams inspect data quality, detect sensitive information, and generate executive-facing governance reports without changing the existing application behavior.

## Architecture

- Web application: Django + Gunicorn
- Task processing: Celery workers and beat
- Message broker: Redis
- Database: PostgreSQL (containerized for local development)
- Static assets: WhiteNoise
- Media storage: local filesystem

## Features

- Dataset upload and validation
- Metadata extraction
- Data quality scoring
- Sensitive data discovery
- Governance report generation
- Background task processing

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template and adjust values:
   ```bash
   copy .env.example .env
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```

## Docker

Run the full stack with Docker Compose:

```bash
docker compose up --build
```

Services:
- web: Django application on port 8001
- worker: Celery worker
- beat: Celery beat scheduler
- db: PostgreSQL
- redis: Redis

## Environment Variables

Key variables:
- DJANGO_SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- DB_ENGINE
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_HOST
- POSTGRES_PORT
- REDIS_URL
- CELERY_BROKER_URL
- CELERY_RESULT_BACKEND

## API Endpoints

- /health/
- /api/health/
- /datasets/
- /datasets/upload/

## Screenshots

- Placeholder: add screenshots to docs/screenshots/

## Deployment

For production, configure a managed PostgreSQL instance, Redis, and environment variables securely. The containerized setup is suitable for deployment platforms that support Docker images and managed services.

