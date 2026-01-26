# Your First Comparison

This guide walks you through creating entities and recording your first comparison.

## Step 1: Create Entities

Entities are the items you want to compare. Create at least two:

```bash
curl -X POST http://localhost:8090/entities/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Pizza", "description": "Classic Italian dish", "image_urls": []}'
```

Response:
```json
{
  "id": 1,
  "name": "Pizza",
  "description": "Classic Italian dish",
  "image_urls": [],
  "rating": 1500.0
}
```

Create another entity:

```bash
curl -X POST http://localhost:8090/entities/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Burger", "description": "American classic", "image_urls": []}'
```

## Step 2: Get a Comparison Pair

Ask the MAB algorithm for the next optimal pair:

```bash
curl http://localhost:8090/mab/next_comparison
```

Response:
```json
{
  "entity1": {"id": 1, "name": "Pizza", "rating": 1500.0, ...},
  "entity2": {"id": 2, "name": "Burger", "rating": 1500.0, ...}
}
```

## Step 3: Submit the Comparison

Record which entity won (based on user preference):

```bash
curl -X POST http://localhost:8090/comparisons/ \
  -H "Content-Type: application/json" \
  -d '{"entity1_id": 1, "entity2_id": 2, "selected_entity_id": 1}'
```

This:

1. Records the comparison
2. Updates Elo ratings for both entities
3. Updates MAB state for future pair selection

Response:
```json
{
  "id": 1,
  "entity1_id": 1,
  "entity2_id": 2,
  "selected_entity_id": 1,
  "created_at": "2024-01-15T10:35:00Z"
}
```

## Step 4: View Rankings

Check the updated leaderboard:

```bash
curl http://localhost:8090/ratings
```

Response:
```json
[
  {"id": 1, "name": "Pizza", "rating": 1516.0, ...},
  {"id": 2, "name": "Burger", "rating": 1484.0, ...}
]
```

The winner's rating increased, the loser's decreased.

## Understanding the Results

### Elo Rating Changes

- **Winner**: +16 points (1500 → 1516)
- **Loser**: -16 points (1500 → 1484)

With the default K-factor (32) and equal starting ratings, each comparison moves ratings by 16 points.

### Rating Interpretation

| Rating Range | Interpretation |
|--------------|----------------|
| 1600+ | Top tier |
| 1500-1600 | Above average |
| 1400-1500 | Below average |
| < 1400 | Bottom tier |

## Next Steps

- Add more entities and comparisons
- Explore the [API Reference](../user-guide/api-reference.md)
- Learn about [Elo ratings](../concepts/elo-rating.md) and [MAB algorithms](../concepts/mab-algorithm.md)
