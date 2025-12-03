# Compere

[![CI](https://github.com/terraprompt/compere/actions/workflows/ci.yml/badge.svg)](https://github.com/terraprompt/compere/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/compere.svg)](https://badge.fury.io/py/compere)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comparative rating system using Multi-Armed Bandit (MAB) algorithms and Elo ratings. Build preference collection systems, leaderboards, and A/B testing workflows with intelligent entity pairing.

## Use Cases

**Human Evaluation & Labeling**
- Collect preference data for ML training (RLHF, reward models)
- A/B test designs, content, or features with human judges
- Build annotation interfaces for pairwise comparisons

**Ranking Systems**
- Product comparison platforms
- Leaderboards for games, content, or competitions
- Recommendation system training data collection

## Features

- **Smart Pairing**: UCB algorithm balances exploration vs exploitation for efficient comparisons
- **Elo Ratings**: Dynamic rating updates with configurable K-factor
- **Cold-Start Handling**: New entities are prioritized for quick integration
- **Dual Mode**: Use as a Python library or REST API
- **Demo UI**: Vue.js interface for interactive simulations

## Quick Start

### Installation

```bash
# Using uv (recommended)
uv add compere

# Using pip
pip install compere
```

### Run the API Server

```bash
# Start server on port 8090
uv run compere --port 8090 --reload
```

API docs available at `http://localhost:8090/docs`

### Run the Demo UI

The demo UI lets you try Compere with pre-built scenarios (restaurants, movies, products, gamers).

```bash
cd compere-ui
npm install
npm run dev
```

Open the displayed URL (usually `http://localhost:3000`) and select a scenario to start comparing.

## Usage

### As a Library

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from compere.modules.database import Base
from compere.modules.models import EntityCreate, ComparisonCreate
from compere.modules.entity import create_entity
from compere.modules.comparison import create_comparison
from compere.modules.rating import get_ratings

# Setup database
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create entities
entity1 = create_entity(EntityCreate(
    name="Option A",
    description="First option to compare"
), db)

entity2 = create_entity(EntityCreate(
    name="Option B",
    description="Second option to compare"
), db)

# Record a comparison (user preferred entity1)
create_comparison(ComparisonCreate(
    entity1_id=entity1.id,
    entity2_id=entity2.id,
    selected_entity_id=entity1.id
), db)

# Get updated rankings
for entity in get_ratings(db):
    print(f"{entity.name}: {entity.rating:.0f}")
```

### As an API

```bash
# Create an entity
curl -X POST http://localhost:8090/entities/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Option A", "description": "First option"}'

# Get next pair to compare (MAB algorithm)
curl http://localhost:8090/mab/next_comparison

# Submit comparison result
curl -X POST http://localhost:8090/comparisons/ \
  -H "Content-Type: application/json" \
  -d '{"entity1_id": 1, "entity2_id": 2, "selected_entity_id": 1}'

# Get leaderboard
curl http://localhost:8090/ratings
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /entities/` | Create entity |
| `GET /entities/` | List entities (with search/pagination) |
| `GET /mab/next_comparison` | Get next pair using UCB algorithm |
| `POST /comparisons/` | Record comparison and update ratings |
| `GET /ratings` | Get leaderboard sorted by rating |

Full API documentation at `/docs` when server is running.

## Configuration

Key environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./compere.db` | Database connection string |
| `ELO_K_FACTOR` | `32.0` | Rating sensitivity |
| `ELO_INITIAL_RATING` | `1500.0` | Starting rating for new entities |
| `UCB_EXPLORATION_CONSTANT` | `1.414` | UCB exploration factor |
| `PAIRING_SIMILARITY_WEIGHT` | `0.4` | Weight for rating similarity in pairing |
| `RECENT_COMPARISON_LIMIT` | `5` | Recent comparisons to exclude |

See [Configuration](docs/configuration.md) for all options including authentication, rate limiting, and pairing weights.

## Development

```bash
# Clone and setup
git clone https://github.com/terraprompt/compere.git
cd compere
uv sync

# Run backend
uv run compere --reload

# Run frontend (separate terminal)
cd compere-ui
npm install
npm run dev

# Run tests
uv run pytest
```

## How It Works

1. **Entity Creation**: Add items to compare (products, options, content)
2. **Smart Pairing**: MAB algorithm selects pairs that maximize information gain
3. **Comparison**: User/evaluator picks a winner
4. **Rating Update**: Elo algorithm adjusts ratings based on outcome
5. **Repeat**: System learns optimal pairings over time

The UCB (Upper Confidence Bound) algorithm ensures:
- New entities get compared quickly (exploration)
- High-uncertainty pairs are prioritized (exploitation)
- Ratings converge efficiently with fewer comparisons

## Documentation

- [Getting Started](docs/getting-started.md) - Installation and first steps
- [API Reference](docs/api-reference.md) - Complete REST API documentation
- [Library Usage](docs/library-usage.md) - Using Compere in Python code
- [Configuration](docs/configuration.md) - Environment variables and options
- [Algorithms](docs/algorithms.md) - How MAB and Elo work

## License

MIT License - see [LICENSE](LICENSE) for details.
