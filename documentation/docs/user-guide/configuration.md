# Configuration

Compere is configured through environment variables. Set these before starting the server.

## Quick Setup

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

## Environment Variables

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./compere.db` | Database connection string |

**Examples:**

=== "SQLite (Development)"

    ```bash
    DATABASE_URL=sqlite:///./compere.db
    ```

=== "PostgreSQL (Production)"

    ```bash
    DATABASE_URL=postgresql://user:password@localhost:5432/compere
    ```

=== "MySQL"

    ```bash
    DATABASE_URL=mysql://user:password@localhost:3306/compere
    ```

### Elo Rating System

| Variable | Default | Description |
|----------|---------|-------------|
| `ELO_K_FACTOR` | `32.0` | Rating sensitivity factor |
| `ELO_INITIAL_RATING` | `1500.0` | Starting rating for new entities |

The K-factor controls how much ratings change after each comparison:

| K-Factor | Use Case |
|----------|----------|
| 40-50 | New systems, rapid convergence needed |
| 32 | Standard (default) |
| 16-24 | Established rankings, stability preferred |

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

!!! note
    Pairing weights should sum to 1.0 for consistent behavior.

### Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_ENABLED` | `false` | Enable JWT authentication |
| `SECRET_KEY` | (none) | JWT signing secret (required if auth enabled) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time |

Generate a secure secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### CORS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | (varies) | Comma-separated allowed origins |

- In development: defaults to `["*"]` (all origins)
- In production: must be explicitly set

```bash
CORS_ORIGINS=https://myapp.com,https://admin.myapp.com
```

### Rate Limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | `false` | Enable rate limiting |
| `RATE_LIMIT_REQUESTS` | `100` | Max requests per window |
| `RATE_LIMIT_WINDOW` | `60` | Window size in seconds |

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `LOG_REQUESTS` | `true` | Log HTTP requests |
| `ENVIRONMENT` | `development` | Environment name |

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## Complete Configuration File

```bash
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
AUTH_ENABLED=true
SECRET_KEY=your-secure-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=https://myapp.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_REQUESTS=true
ENVIRONMENT=production
```

## Frontend Configuration

The Vue.js frontend uses a separate `.env` file in `compere-ui/`:

```bash
VITE_API_BASE_URL=http://localhost:8090
```

## Production Recommendations

1. **Use PostgreSQL** for production workloads
2. **Enable authentication** with a strong secret key
3. **Enable rate limiting** to prevent abuse
4. **Set `ENVIRONMENT=production`** for secure error handling
5. **Configure CORS** explicitly (don't use `*`)
6. **Set `LOG_LEVEL=WARNING`** to reduce log volume
7. **Use a reverse proxy** (nginx, Caddy) for HTTPS
