# Configuration

Compere is configured through environment variables. Set these before starting the server.

## Environment Variables

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./compere.db` | Database connection string |

**Examples:**
```bash
# SQLite (default, good for development)
export DATABASE_URL=sqlite:///./compere.db

# PostgreSQL (recommended for production)
export DATABASE_URL=postgresql://user:password@localhost:5432/compere

# MySQL
export DATABASE_URL=mysql://user:password@localhost:3306/compere
```

### Elo Rating System

| Variable | Default | Description |
|----------|---------|-------------|
| `ELO_K_FACTOR` | `32.0` | Rating sensitivity factor |
| `ELO_INITIAL_RATING` | `1500.0` | Starting rating for new entities |

The K-factor controls how much ratings change after each comparison:
- **Higher K (40-50)**: Ratings change quickly, good for volatile rankings
- **Default K (32)**: Balanced, standard chess rating
- **Lower K (16-24)**: Ratings change slowly, good for stable rankings

### UCB/MAB Algorithm

| Variable | Default | Description |
|----------|---------|-------------|
| `UCB_EXPLORATION_CONSTANT` | `1.414` | Exploration factor (sqrt(2)) |
| `UCB_UNEXPLORED_WEIGHT` | `1000.0` | Weight for entities with no comparisons |

The exploration constant controls the exploration-exploitation tradeoff:
- **Higher values (2.0+)**: More exploration of uncertain entities
- **Default (1.414)**: Balanced (theoretically optimal)
- **Lower values (0.5-1.0)**: More exploitation of known good entities

### Entity Pairing

| Variable | Default | Description |
|----------|---------|-------------|
| `PAIRING_UCB_WEIGHT` | `0.3` | Weight for UCB score in pairing |
| `PAIRING_SIMILARITY_WEIGHT` | `0.4` | Weight for rating similarity |
| `PAIRING_RANDOM_WEIGHT` | `0.3` | Weight for random factor |
| `PAIRING_RATING_THRESHOLD` | `200.0` | Rating difference for similarity bonus |
| `RECENT_COMPARISON_LIMIT` | `5` | Recent comparisons to exclude |

Pairing weights control how the second entity is selected:
- **UCB weight**: Favors entities needing more comparisons
- **Similarity weight**: Favors entities with similar ratings (more informative)
- **Random weight**: Adds variety to prevent repetitive pairings

Weights should sum to 1.0 for consistent behavior.

### Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_ENABLED` | `false` | Enable JWT authentication |
| `SECRET_KEY` | (required if auth enabled) | JWT signing secret |

When authentication is enabled:
```bash
export AUTH_ENABLED=true
export SECRET_KEY=your-very-secure-secret-key-here
```

Generate a secure secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Rate Limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | `false` | Enable rate limiting |
| `RATE_LIMIT_REQUESTS` | `100` | Max requests per window |
| `RATE_LIMIT_WINDOW` | `60` | Window size in seconds |

Example (100 requests per minute):
```bash
export RATE_LIMIT_ENABLED=true
export RATE_LIMIT_REQUESTS=100
export RATE_LIMIT_WINDOW=60
```

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `LOG_REQUESTS` | `true` | Log HTTP requests |
| `ENVIRONMENT` | `development` | Environment name |

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## Configuration File

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://localhost/compere

# Elo Rating System
ELO_K_FACTOR=32.0
ELO_INITIAL_RATING=1500.0

# UCB/MAB Algorithm
UCB_EXPLORATION_CONSTANT=1.414
UCB_UNEXPLORED_WEIGHT=1000.0

# Entity Pairing (weights should sum to 1.0)
PAIRING_UCB_WEIGHT=0.3
PAIRING_SIMILARITY_WEIGHT=0.4
PAIRING_RANDOM_WEIGHT=0.3
PAIRING_RATING_THRESHOLD=200.0
RECENT_COMPARISON_LIMIT=5

# Authentication
AUTH_ENABLED=false
SECRET_KEY=change-me-in-production

# Rate Limiting
RATE_LIMIT_ENABLED=false
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_REQUESTS=true
ENVIRONMENT=development
```

## Frontend Configuration

The Vue.js frontend uses a separate `.env` file in `compere-ui/`:

```env
VITE_API_BASE_URL=http://localhost:8090
```

Update this if your backend runs on a different host/port.

## Database Setup

### SQLite (Default)

No setup required. The database file is created automatically.

To reset:
```bash
rm compere.db
```

### PostgreSQL

```bash
# Create database
createdb compere

# Set connection string
export DATABASE_URL=postgresql://user:password@localhost:5432/compere
```

### MySQL

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE compere;"

# Set connection string
export DATABASE_URL=mysql://user:password@localhost:3306/compere
```

## Production Recommendations

1. **Use PostgreSQL** for production workloads
2. **Enable authentication** with a strong secret key
3. **Enable rate limiting** to prevent abuse
4. **Set `LOG_LEVEL=WARNING`** to reduce log volume
5. **Use a reverse proxy** (nginx, Caddy) for HTTPS
6. **Run with gunicorn** for multiple workers:

```bash
gunicorn compere.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Docker

Example `docker-compose.yml`:

```yaml
version: '3.8'
services:
  compere:
    build: .
    ports:
      - "8090:8090"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/compere
      - AUTH_ENABLED=true
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=compere
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```
