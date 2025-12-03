# Getting Started

This guide walks you through installing Compere and running your first comparison.

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Node.js 18+ (for the demo UI)

## Installation

### Using uv (Recommended)

```bash
uv add compere
```

### Using pip

```bash
pip install compere
```

### From Source

```bash
git clone https://github.com/terraprompt/compere.git
cd compere
uv sync
```

## Running the API Server

Start the server with:

```bash
uv run compere --port 8090 --reload
```

Options:
- `--host`: Bind address (default: `127.0.0.1`)
- `--port`: Port number (default: `8000`)
- `--reload`: Auto-reload on code changes (development)

Once running, visit `http://localhost:8090/docs` for the interactive API documentation.

## Running the Demo UI

The demo UI provides a visual interface to experiment with Compere.

```bash
cd compere-ui
npm install
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

## Your First Comparison

### Step 1: Create Entities

Entities are the items you want to compare. Create at least two:

```bash
curl -X POST http://localhost:8090/entities/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Pizza", "description": "Classic Italian dish"}'

curl -X POST http://localhost:8090/entities/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Burger", "description": "American classic"}'
```

### Step 2: Get a Comparison Pair

Ask the MAB algorithm for the next optimal pair:

```bash
curl http://localhost:8090/mab/next_comparison
```

Response:
```json
{
  "entity1": {"id": 1, "name": "Pizza", "rating": 1500},
  "entity2": {"id": 2, "name": "Burger", "rating": 1500}
}
```

### Step 3: Submit the Comparison

Record which entity won (user preference):

```bash
curl -X POST http://localhost:8090/comparisons/ \
  -H "Content-Type: application/json" \
  -d '{"entity1_id": 1, "entity2_id": 2, "selected_entity_id": 1}'
```

### Step 4: View Rankings

Check the updated leaderboard:

```bash
curl http://localhost:8090/ratings
```

The winner's rating increases, the loser's decreases.

## Database Setup

By default, Compere uses SQLite stored in `./compere.db`. This file is created automatically.

For production, use PostgreSQL or MySQL. See [Configuration](configuration.md) for details.

## Next Steps

- [API Reference](api-reference.md) - Full endpoint documentation
- [Library Usage](library-usage.md) - Using Compere in Python code
- [Configuration](configuration.md) - Environment variables and options
- [Algorithms](algorithms.md) - How MAB and Elo work
