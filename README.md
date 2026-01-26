# Compere

**Intelligent pairwise comparisons. Better rankings with fewer votes.**

[![CI](https://github.com/skelf-research/compere/actions/workflows/ci.yml/badge.svg)](https://github.com/skelf-research/compere/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/compere.svg)](https://badge.fury.io/py/compere)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Docs](https://img.shields.io/badge/docs-skelfresearch.com-blue)](https://docs.skelfresearch.com/compere)

Compere combines **Multi-Armed Bandit algorithms** with **Elo ratings** to build ranking systems that learn which comparisons matter most. Get accurate rankings faster by asking the right questions.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Create    │────▶│   Compare   │────▶│    Rank     │
│  Entities   │     │  (MAB picks │     │ (Elo rates) │
└─────────────┘     │   smartly)  │     └─────────────┘
                    └─────────────┘
```

---

## Quick Start

### Install

```bash
pip install compere
# or with uv
uv add compere
```

### Run

```bash
# Start the API server
compere --port 8090

# Or with uv
uv run compere --port 8090 --reload
```

Open http://localhost:8090/docs for interactive API documentation.

### Try it

```bash
# Create two entities
curl -X POST localhost:8090/entities/ -H "Content-Type: application/json" \
  -d '{"name": "Option A", "description": "First choice"}'

curl -X POST localhost:8090/entities/ -H "Content-Type: application/json" \
  -d '{"name": "Option B", "description": "Second choice"}'

# Get the next pair to compare (MAB algorithm picks optimally)
curl localhost:8090/mab/next_comparison

# Submit a comparison (user preferred entity 1)
curl -X POST localhost:8090/comparisons/ -H "Content-Type: application/json" \
  -d '{"entity1_id": 1, "entity2_id": 2, "selected_entity_id": 1}'

# View rankings
curl localhost:8090/ratings
```

---

## Use Cases

| Use Case | Description |
|----------|-------------|
| **RLHF Data Collection** | Gather human preferences efficiently for training reward models |
| **A/B Testing** | Compare designs, content, or features with statistical rigor |
| **Leaderboards** | Build dynamic rankings for games, products, or competitions |
| **Annotation Tools** | Create labeling interfaces for pairwise preference data |
| **Recommendation Training** | Collect comparison data to train recommendation systems |

---

## Use as a Library

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from compere.modules.database import Base
from compere.modules.entity import create_entity
from compere.modules.comparison import create_comparison
from compere.modules.rating import get_ratings
from compere.modules.models import EntityCreate, ComparisonCreate

# Setup
engine = create_engine("sqlite:///./rankings.db")
Base.metadata.create_all(bind=engine)
db = sessionmaker(bind=engine)()

# Create entities to rank
pizza = create_entity(db, EntityCreate(name="Pizza", description="Classic favorite"))
sushi = create_entity(db, EntityCreate(name="Sushi", description="Fresh and healthy"))
tacos = create_entity(db, EntityCreate(name="Tacos", description="Mexican street food"))

# Record comparisons (pizza beats sushi, tacos beat pizza)
create_comparison(ComparisonCreate(
    entity1_id=pizza.id, entity2_id=sushi.id, selected_entity_id=pizza.id
), db)
create_comparison(ComparisonCreate(
    entity1_id=pizza.id, entity2_id=tacos.id, selected_entity_id=tacos.id
), db)

# Get rankings
for entity in get_ratings(db):
    print(f"{entity.name}: {entity.rating:.0f}")
# Output:
# Tacos: 1516
# Pizza: 1500
# Sushi: 1484
```

---

## Docker

```bash
# Quick start with Docker Compose
curl -O https://raw.githubusercontent.com/skelf-research/compere/main/docker-compose.yml
docker compose up -d

# API available at http://localhost:8090
```

Or build locally:

```bash
git clone https://github.com/skelf-research/compere.git
cd compere
docker compose up -d
```

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/entities/` | POST | Create a new entity |
| `/entities/` | GET | List entities (search, pagination) |
| `/entities/{id}` | GET | Get entity by ID |
| `/entities/{id}` | PUT | Update entity |
| `/entities/{id}` | DELETE | Delete entity |
| `/mab/next_comparison` | GET | Get optimal pair using UCB algorithm |
| `/comparisons/next` | GET | Get pair using similarity-based selection |
| `/comparisons/` | POST | Record comparison result |
| `/comparisons/` | GET | List comparison history |
| `/ratings` | GET | Get leaderboard (sorted by rating) |
| `/health` | GET | Health check |
| `/health/ready` | GET | Readiness check (with DB) |

Full interactive docs at `/docs` when running.

---

## Configuration

Configure via environment variables or `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/compere  # Default: sqlite:///./compere.db

# Elo Rating
ELO_K_FACTOR=32.0           # Rating sensitivity (higher = more volatile)
ELO_INITIAL_RATING=1500.0   # Starting rating for new entities

# MAB Algorithm
UCB_EXPLORATION_CONSTANT=1.414   # Exploration vs exploitation balance
UCB_UNEXPLORED_WEIGHT=1000.0     # Priority for new entities

# Security (optional)
AUTH_ENABLED=false          # Enable JWT authentication
SECRET_KEY=your-secret      # Required if AUTH_ENABLED=true
CORS_ORIGINS=http://localhost:3000,https://app.example.com

# Rate Limiting (optional)
RATE_LIMIT_ENABLED=false
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

See [`.env.example`](.env.example) for all options.

---

## How It Works

### The Problem
Traditional ranking requires O(n²) comparisons. With 100 items, that's 4,950 comparisons!

### The Solution
Compere uses **Upper Confidence Bound (UCB)** to pick comparisons that maximize information gain:

1. **Exploration**: New entities get compared quickly
2. **Exploitation**: High-uncertainty pairs are prioritized
3. **Convergence**: Accurate rankings with ~10x fewer comparisons

### The Algorithm

```
UCB Score = win_rate + c * sqrt(ln(total_comparisons) / entity_comparisons)
            ────────   ─────────────────────────────────────────────────────
            exploit                    explore
```

Combined with **Elo ratings** for smooth, interpretable scores:

```
New Rating = Old Rating + K * (Actual - Expected)

where Expected = 1 / (1 + 10^((opponent_rating - rating) / 400))
```

---

## Development

```bash
# Clone
git clone https://github.com/skelf-research/compere.git
cd compere

# Install dependencies
uv sync

# Run backend (auto-reload)
uv run compere --reload

# Run tests
uv run pytest

# Run linter
uvx ruff check .

# Run frontend demo (optional)
cd compere-ui && npm install && npm run dev
```

### Project Structure

```
compere/
├── compere/
│   ├── main.py              # FastAPI app entry point
│   └── modules/
│       ├── auth.py          # JWT authentication
│       ├── comparison.py    # Comparison CRUD
│       ├── config.py        # Configuration management
│       ├── database.py      # SQLAlchemy setup
│       ├── entity.py        # Entity CRUD
│       ├── errors.py        # Error handling
│       ├── mab.py           # Multi-Armed Bandit (UCB)
│       ├── middleware.py    # Rate limiting, logging
│       ├── models.py        # SQLAlchemy + Pydantic models
│       ├── rating.py        # Elo rating calculations
│       └── similarity.py    # Entity pairing by similarity
├── compere-ui/              # Vue.js demo interface
├── tests/                   # pytest test suite
├── documentation/           # MkDocs documentation
└── docker-compose.yml       # Docker deployment
```

---

## Documentation

Full documentation available at **[docs.skelfresearch.com/compere](https://docs.skelfresearch.com/compere)**

- [Getting Started](https://docs.skelfresearch.com/compere/getting-started/installation/) - Installation and first steps
- [API Reference](https://docs.skelfresearch.com/compere/user-guide/api-reference/) - Complete endpoint documentation
- [Library Usage](https://docs.skelfresearch.com/compere/user-guide/library-usage/) - Using Compere in Python
- [Configuration](https://docs.skelfresearch.com/compere/user-guide/configuration/) - All configuration options
- [Elo Rating](https://docs.skelfresearch.com/compere/concepts/elo-rating/) - How Elo ratings work
- [MAB Algorithm](https://docs.skelfresearch.com/compere/concepts/mab-algorithm/) - UCB algorithm explained
- [Docker Deployment](https://docs.skelfresearch.com/compere/deployment/docker/) - Container deployment guide

---

## Contributing

Contributions welcome! Please read our contributing guidelines and submit PRs to the `main` branch.

```bash
# Setup development environment
git clone https://github.com/skelf-research/compere.git
cd compere
uv sync --all-extras

# Make changes, then run tests
uv run pytest
uvx ruff check .
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built for humans who rank things.</sub>
</p>
