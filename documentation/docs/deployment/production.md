# Production Guide

Best practices for running Compere in production.

## Security Checklist

- [ ] Set a strong `SECRET_KEY`
- [ ] Enable `AUTH_ENABLED=true`
- [ ] Configure `CORS_ORIGINS` explicitly (no wildcards)
- [ ] Enable `RATE_LIMIT_ENABLED=true`
- [ ] Set `ENVIRONMENT=production`
- [ ] Use HTTPS (via reverse proxy)
- [ ] Use PostgreSQL (not SQLite)

## Generate Secure Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database Setup

### PostgreSQL (Recommended)

```bash
# Create database
createdb compere

# Set connection string
DATABASE_URL=postgresql://user:password@localhost:5432/compere
```

### Connection Pooling

For high-traffic deployments, use PgBouncer or similar:

```bash
DATABASE_URL=postgresql://user:password@pgbouncer:6432/compere
```

## Reverse Proxy

### Nginx Configuration

```nginx
upstream compere {
    server 127.0.0.1:8090;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://compere;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Caddy Configuration

```
api.example.com {
    reverse_proxy localhost:8090
}
```

## Multiple Workers

For production, run with multiple workers:

```bash
# Using gunicorn
gunicorn compere.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8090

# Using uvicorn directly
uvicorn compere.main:app --workers 4 --host 0.0.0.0 --port 8090
```

Rule of thumb: `workers = (2 * CPU cores) + 1`

## Environment Configuration

Production `.env` file:

```bash
# Database
DATABASE_URL=postgresql://compere:password@localhost:5432/compere

# Security
SECRET_KEY=your-64-character-secret-key-here
AUTH_ENABLED=true
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS - explicit origins only
CORS_ORIGINS=https://app.example.com,https://admin.example.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=WARNING
LOG_REQUESTS=true
ENVIRONMENT=production
```

## Monitoring

### Health Checks

Monitor these endpoints:

- `GET /health` - Basic health check
- `GET /health/ready` - Database connectivity

### Metrics to Track

- Response times (p50, p95, p99)
- Error rates
- Request volume
- Database connection pool usage
- Memory usage

### Recommended Tools

- **Prometheus + Grafana**: Metrics and visualization
- **Sentry**: Error tracking
- **ELK Stack**: Log aggregation

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump -h localhost -U compere compere | gzip > /backups/compere_$DATE.sql.gz

# Keep last 30 days
find /backups -name "compere_*.sql.gz" -mtime +30 -delete
```

### Point-in-Time Recovery

Enable WAL archiving for PostgreSQL:

```sql
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command = 'cp %p /archive/%f';
```

## Scaling Considerations

### Horizontal Scaling

1. Use a shared database (PostgreSQL)
2. Stateless backend instances
3. Load balancer (nginx, HAProxy, cloud LB)

### Vertical Scaling

| Users | Recommended Setup |
|-------|-------------------|
| < 100 | 1 CPU, 512MB RAM |
| 100-1000 | 2 CPU, 1GB RAM |
| 1000-10000 | 4 CPU, 2GB RAM, connection pooling |
| > 10000 | Multiple instances, caching layer |

## Maintenance

### Zero-Downtime Deployments

1. Deploy new version to new containers
2. Health check new containers
3. Switch traffic
4. Drain old containers

### Database Migrations

The database schema auto-creates on startup. For schema changes:

1. Backup database
2. Test migration on staging
3. Apply during low-traffic period
4. Verify integrity
