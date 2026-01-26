# FAQ

Frequently asked questions about Compere.

## General

### What is Compere?

Compere is a comparative rating system that combines Elo ratings with Multi-Armed Bandit algorithms to efficiently rank entities through pairwise comparisons.

### What can I use it for?

- Product rankings based on user preferences
- Content moderation and quality assessment
- A/B testing with pairwise comparisons
- Building recommendation systems
- Survey research and preference collection
- Gaming/esports player rankings

### Is Compere free?

Yes, Compere is open source under the MIT License.

## Installation

### What Python version do I need?

Python 3.11 or higher is required.

### How do I install Compere?

```bash
# Using uv (recommended)
uv add compere

# Using pip
pip install compere
```

### Can I use Compere without the web server?

Yes, you can use Compere as a Python library:

```python
from compere.modules.entity import create_entity
from compere.modules.rating import get_ratings
```

## API

### How do I get the next comparison pair?

```bash
curl http://localhost:8090/mab/next_comparison
```

### How do I record a comparison?

```bash
curl -X POST http://localhost:8090/comparisons/ \
  -H "Content-Type: application/json" \
  -d '{"entity1_id": 1, "entity2_id": 2, "selected_entity_id": 1}'
```

### How do I get the rankings?

```bash
curl http://localhost:8090/ratings
```

## Algorithms

### What is the Elo rating system?

Elo is a method for calculating relative skill levels. Originally developed for chess, it updates ratings based on comparison outcomes and expected results.

### What is UCB (Upper Confidence Bound)?

UCB is a Multi-Armed Bandit algorithm that balances exploration (trying less-compared entities) with exploitation (focusing on uncertain rankings).

### How many comparisons do I need?

It depends on the number of entities and desired accuracy. UCB typically requires O(N log N) comparisons for N entities, compared to O(N²) for random pairing.

### Can I adjust the algorithm parameters?

Yes, see the [Configuration](user-guide/configuration.md) page for environment variables like `ELO_K_FACTOR` and `UCB_EXPLORATION_CONSTANT`.

## Database

### What databases are supported?

- SQLite (default, good for development)
- PostgreSQL (recommended for production)
- MySQL

### How do I switch to PostgreSQL?

```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/compere
```

### How do I reset the database?

For SQLite:
```bash
rm compere.db
```

For PostgreSQL:
```bash
dropdb compere && createdb compere
```

## Authentication

### Is authentication required?

No, authentication is disabled by default. Enable it with:

```bash
AUTH_ENABLED=true
SECRET_KEY=your-secure-key
```

### How do I create the first user?

The first user created is automatically a superuser:

```bash
curl -X POST http://localhost:8090/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "securepassword"}'
```

## Troubleshooting

### Why am I getting CORS errors?

Set the `CORS_ORIGINS` environment variable:

```bash
CORS_ORIGINS=http://localhost:3000
```

### Why am I getting "no such table" errors?

The database tables may not be created. Restart the server:

```bash
uv run compere --reload
```

### Why is the API slow?

- Use PostgreSQL instead of SQLite for production
- Enable connection pooling
- Check database indexes

### How do I get help?

1. Check this FAQ
2. Read the [Troubleshooting](deployment/troubleshooting.md) guide
3. Search [GitHub Issues](https://github.com/terraprompt/compere/issues)
4. Open a new issue if needed

## Frontend

### Is a frontend included?

Yes, a Vue.js demo UI is available in the `compere-ui/` directory.

### How do I run the frontend?

```bash
cd compere-ui
npm install
npm run dev
```

### Can I use my own frontend?

Yes, Compere provides a REST API that works with any frontend framework.

## Contributing

### How can I contribute?

See the [Contributing](development/contributing.md) guide.

### What's the code style?

We use ruff for linting. Run `uvx ruff check .` before submitting PRs.

### Are there tests?

Yes, tests are in the `tests/` directory. Run with `uv run pytest`.
