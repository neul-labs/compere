# Troubleshooting

Common issues and solutions when deploying Compere.

## Common Issues

### "No such table" Error

**Symptom**: Database table not found errors on startup.

**Causes**:

1. Models not imported in `main.py`
2. Database needs recreation
3. Database URL mismatch

**Solutions**:

```bash
# Delete and recreate SQLite database
rm compere.db
uv run compere

# For PostgreSQL, check connection string
echo $DATABASE_URL
```

### Port Already in Use

**Symptom**: `Address already in use` error.

**Solution**:

```bash
# Find process using port
lsof -ti:8090

# Kill the process
lsof -ti:8090 | xargs kill -9

# Or use a different port
uv run compere --port 8091
```

### CORS Errors

**Symptom**: Browser shows CORS errors, API calls fail.

**Causes**:

1. Frontend origin not in `CORS_ORIGINS`
2. CORS not configured at all
3. Reverse proxy stripping headers

**Solutions**:

```bash
# Set allowed origins
CORS_ORIGINS=http://localhost:3000,https://myapp.com

# For development, use wildcard
CORS_ORIGINS=*
```

### Authentication Failures

**Symptom**: 401 Unauthorized errors.

**Causes**:

1. `SECRET_KEY` not set
2. Token expired
3. Wrong credentials

**Solutions**:

```bash
# Ensure SECRET_KEY is set
echo $SECRET_KEY

# Generate new secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check auth is enabled
echo $AUTH_ENABLED
```

### Database Connection Issues

**Symptom**: Connection refused or timeout errors.

**Solutions**:

```bash
# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1"

# Check Docker network (if using Docker)
docker-compose exec compere ping db

# Verify database exists
psql -h localhost -U postgres -l
```

### Rate Limit Exceeded

**Symptom**: 429 Too Many Requests errors.

**Solutions**:

```bash
# Increase limit
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW=60

# Or disable temporarily
RATE_LIMIT_ENABLED=false
```

### Memory Issues

**Symptom**: Container killed (OOMKilled) or slow performance.

**Solutions**:

```bash
# Check memory usage
docker stats

# Increase container memory
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 1G
```

### Slow Queries

**Symptom**: API responses are slow.

**Solutions**:

1. Add database indexes (already included)
2. Enable connection pooling
3. Check query patterns

```sql
-- Check slow queries (PostgreSQL)
SELECT query, calls, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## Debugging Tips

### Enable Debug Logging

```bash
LOG_LEVEL=DEBUG
```

### Check Container Logs

```bash
docker-compose logs -f compere
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8090/health

# Readiness check
curl http://localhost:8090/health/ready

# Create test entity
curl -X POST http://localhost:8090/entities/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "description": "Test entity", "image_urls": []}'
```

### Database Inspection

```bash
# SQLite
sqlite3 compere.db ".tables"
sqlite3 compere.db "SELECT * FROM entities"

# PostgreSQL
docker-compose exec db psql -U compere -c "SELECT * FROM entities"
```

## Getting Help

1. Check the [GitHub Issues](https://github.com/terraprompt/compere/issues)
2. Search existing issues before creating new ones
3. Include:
   - Compere version
   - Python version
   - Full error message
   - Steps to reproduce
