# Quick Start

## Start the Server

=== "Using uv"

    ```bash
    uv run compere --port 8090 --reload
    ```

=== "Direct execution"

    ```bash
    compere --port 8090 --reload
    ```

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `8000` | Port number |
| `--reload` | `false` | Auto-reload on code changes |

## Explore the API

Once running, visit these endpoints:

- **Swagger UI**: [http://localhost:8090/docs](http://localhost:8090/docs)
- **ReDoc**: [http://localhost:8090/redoc](http://localhost:8090/redoc)
- **OpenAPI JSON**: [http://localhost:8090/openapi.json](http://localhost:8090/openapi.json)

## Health Check

Verify the server is running:

```bash
curl http://localhost:8090/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "0.1.0"
}
```

## Start the Demo UI (Optional)

In a separate terminal:

```bash
cd compere-ui
npm run dev
```

Open the displayed URL (usually `http://localhost:3000`).

### Demo Scenarios

The UI includes pre-built scenarios:

| Scenario | Description |
|----------|-------------|
| Restaurants | Compare dining establishments |
| Movies | Rank films by preference |
| Products | Tech product comparisons |
| Gamers | Esports player rankings |

Select a scenario, click "Load Scenario", and start making comparisons.

## Next Steps

- [First Comparison](first-comparison.md) - Create entities and record your first comparison
- [API Reference](../user-guide/api-reference.md) - Full endpoint documentation
