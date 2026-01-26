# Docker Deployment

Deploy Compere using Docker and Docker Compose.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/terraprompt/compere.git
cd compere

# Create environment file
cp .env.example .env

# Edit .env and set SECRET_KEY
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"

# Start services
docker-compose up -d
```

## Docker Compose Configuration

The default `docker-compose.yml` includes:

- **compere**: Backend API service
- **db**: PostgreSQL database
- **ui**: Frontend (optional, use `--profile with-ui`)

### Basic Usage

```bash
# Start backend only
docker-compose up -d

# Start with frontend
docker-compose --profile with-ui up -d

# View logs
docker-compose logs -f compere

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Environment Variables

Set these in your `.env` file:

```bash
# Required
SECRET_KEY=your-secure-secret-key

# Optional
POSTGRES_PASSWORD=compere
AUTH_ENABLED=false
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_ENABLED=true
LOG_LEVEL=INFO
ENVIRONMENT=production
```

## Building Images

### Backend

```bash
docker build -t compere:latest .
```

### Frontend

```bash
docker build -t compere-ui:latest ./compere-ui
```

## Production Docker Compose

For production, create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  compere:
    image: compere:latest
    restart: always
    environment:
      - DATABASE_URL=postgresql://compere:${POSTGRES_PASSWORD}@db:5432/compere
      - SECRET_KEY=${SECRET_KEY}
      - AUTH_ENABLED=true
      - CORS_ORIGINS=${CORS_ORIGINS}
      - RATE_LIMIT_ENABLED=true
      - ENVIRONMENT=production
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

  db:
    image: postgres:15-alpine
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

volumes:
  postgres_data:
```

Run with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Health Checks

The container includes health checks:

```bash
# Check container health
docker-compose ps

# Manual health check
curl http://localhost:8090/health
curl http://localhost:8090/health/ready
```

## Scaling

For horizontal scaling, use multiple backend instances behind a load balancer:

```yaml
services:
  compere:
    deploy:
      replicas: 3
```

!!! warning
    When scaling, ensure all instances share the same database and use sticky sessions if needed.

## Persistent Storage

The PostgreSQL data is stored in a named volume:

```yaml
volumes:
  postgres_data:
```

To backup:

```bash
docker-compose exec db pg_dump -U compere compere > backup.sql
```

To restore:

```bash
cat backup.sql | docker-compose exec -T db psql -U compere compere
```

## Networking

By default, services communicate on an internal Docker network. Only expose necessary ports:

```yaml
services:
  compere:
    ports:
      - "8090:8090"  # Expose to host

  db:
    # No ports exposed (internal only)
```

## Logging

View logs:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f compere

# Last 100 lines
docker-compose logs --tail=100 compere
```

For production logging, consider:

- Log aggregation (ELK, Loki)
- Structured JSON logging
- Log rotation
