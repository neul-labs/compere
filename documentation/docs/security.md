# Security

Security best practices and policies for Compere.

## Security Policy

### Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes |

### Reporting Vulnerabilities

Please report security vulnerabilities by emailing **security@terraprompt.com**.

**Do NOT** open public issues for security vulnerabilities.

We will:

1. Acknowledge receipt within 48 hours
2. Investigate and provide an initial assessment within 1 week
3. Work with you on a fix and coordinated disclosure

## Production Security Checklist

### Required

- [ ] **Set SECRET_KEY**: Generate a secure 32+ character key
- [ ] **Enable AUTH**: Set `AUTH_ENABLED=true`
- [ ] **Configure CORS**: Set explicit origins (no wildcards)
- [ ] **Use HTTPS**: Deploy behind a TLS-enabled reverse proxy
- [ ] **Use PostgreSQL**: Don't use SQLite in production

### Recommended

- [ ] **Enable rate limiting**: Prevent abuse
- [ ] **Set ENVIRONMENT=production**: Hides detailed error messages
- [ ] **Regular backups**: Automated database backups
- [ ] **Monitor logs**: Track authentication failures

## Configuration

### Generate Secure Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output: `xK8vJ2mN7pQ9rS3tW6yZ1aB4cD5eF8gH`

!!! danger
    Never commit secrets to version control. Use environment variables or secret management services.

### Environment Variables

```bash
# Required for production
SECRET_KEY=your-very-long-secure-secret-key
AUTH_ENABLED=true

# Recommended
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_ENABLED=true
ENVIRONMENT=production
```

## Authentication

### JWT Tokens

- Tokens expire after 30 minutes (configurable)
- Tokens are signed with HS256 algorithm
- Store tokens securely (httpOnly cookies recommended)

### Password Security

- Passwords are hashed using bcrypt
- Minimum entropy is not enforced (implement in your application)
- First user created is automatically a superuser

### API Security

```bash
# Authenticated request
curl -H "Authorization: Bearer <token>" http://localhost:8090/auth/users/me
```

## CORS Configuration

### Development

```bash
# Allow all origins (development only!)
CORS_ORIGINS=*
```

### Production

```bash
# Explicit origins only
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

!!! warning
    Never use `CORS_ORIGINS=*` in production. This allows any website to make API requests.

## Rate Limiting

Prevent abuse with rate limiting:

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100  # requests per window
RATE_LIMIT_WINDOW=60     # window in seconds
```

Rate limit headers are included in responses:

- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## Error Handling

### Development Mode

Detailed error messages are shown:

```json
{
  "detail": "Database error: (sqlite3.IntegrityError) UNIQUE constraint failed"
}
```

### Production Mode

Generic error messages protect internals:

```json
{
  "detail": "An internal error occurred. Please try again later."
}
```

Set `ENVIRONMENT=production` to enable safe error messages.

## Database Security

### Connection Strings

Never expose credentials in logs or code:

```bash
# Good - use environment variable
DATABASE_URL=${DATABASE_URL}

# Bad - hardcoded credentials
DATABASE_URL=postgresql://user:password@host/db
```

### PostgreSQL Best Practices

1. Use a dedicated database user with minimal privileges
2. Enable SSL/TLS for connections
3. Use connection pooling (PgBouncer)
4. Regular security updates

## Deployment Security

### Docker

- Use non-root user (already configured)
- Don't expose database ports externally
- Use secrets management for sensitive values

### Reverse Proxy

Always deploy behind a reverse proxy with:

- TLS termination
- Request size limits
- Header security (X-Frame-Options, etc.)

### Example Nginx Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## Logging

### What's Logged

- Request method, path, status code
- Client IP addresses
- Authentication failures
- Database errors (server-side only)

### What's NOT Logged

- Passwords
- JWT tokens
- Request/response bodies

### Log Retention

Implement log rotation and retention policies based on your compliance requirements.
