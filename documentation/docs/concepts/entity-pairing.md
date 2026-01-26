# Entity Pairing

After selecting the first entity using UCB, Compere uses a multi-factor approach to select the second entity for comparison.

## Pairing Strategy

The second entity is chosen using a composite score:

| Factor | Default Weight | Purpose |
|--------|----------------|---------|
| UCB Score | 30% | Exploration value |
| Rating Similarity | 40% | Informative comparisons |
| Random | 30% | Variety |

## How It Works

```python
for entity in remaining_entities:
    score = 0

    # Factor 1: UCB score (exploration value)
    score += ucb_scores.get(entity.id, 0) * 0.3

    # Factor 2: Rating similarity (more informative comparisons)
    rating_diff = abs(entity1.rating - entity.rating)
    if rating_diff < 200:
        score += (200 - rating_diff) / 200 * 0.4

    # Factor 3: Randomness for variety
    score += random.random() * 0.3
```

## Why Rating Similarity Matters

Comparing a 1600-rated entity vs 1580-rated entity is more informative than 1600 vs 1200:

- **Close ratings**: Outcome is uncertain, more information gained
- **Distant ratings**: Outcome is predictable, less information gained

The default threshold is 200 rating points.

## Recent Comparison Exclusion

To prevent repetitive pairings, Compere excludes recent opponents:

```python
recent_comparisons = db.query(Comparison).filter(
    (Comparison.entity1_id == entity1.id) |
    (Comparison.entity2_id == entity1.id)
).order_by(Comparison.created_at.desc()).limit(5).all()

# Exclude recently compared opponents
non_recent = [e for e in remaining if e.id not in recent_opponent_ids]
```

The last 5 opponents are excluded (when alternatives exist).

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PAIRING_UCB_WEIGHT` | `0.3` | Weight for UCB score |
| `PAIRING_SIMILARITY_WEIGHT` | `0.4` | Weight for rating similarity |
| `PAIRING_RANDOM_WEIGHT` | `0.3` | Weight for random factor |
| `PAIRING_RATING_THRESHOLD` | `200.0` | Rating difference threshold |
| `RECENT_COMPARISON_LIMIT` | `5` | Recent comparisons to exclude |

!!! tip
    Weights should sum to 1.0 for consistent behavior.

## Tuning Guidelines

### More Exploration

Increase `PAIRING_UCB_WEIGHT`:

```bash
PAIRING_UCB_WEIGHT=0.5
PAIRING_SIMILARITY_WEIGHT=0.3
PAIRING_RANDOM_WEIGHT=0.2
```

### More Informative Comparisons

Increase `PAIRING_SIMILARITY_WEIGHT`:

```bash
PAIRING_UCB_WEIGHT=0.2
PAIRING_SIMILARITY_WEIGHT=0.6
PAIRING_RANDOM_WEIGHT=0.2
```

### More Variety

Increase `PAIRING_RANDOM_WEIGHT`:

```bash
PAIRING_UCB_WEIGHT=0.3
PAIRING_SIMILARITY_WEIGHT=0.3
PAIRING_RANDOM_WEIGHT=0.4
```

## Similarity Matching Alternative

The `/dissimilar_entities` endpoint uses cosine similarity instead of the multi-factor approach:

- Finds entities that are most **dissimilar** (different categories, characteristics)
- Useful for ensuring diverse coverage
- Currently uses placeholder embeddings (random vectors)

For production, replace with real embeddings from:

- Text embeddings (OpenAI, Sentence Transformers)
- Image embeddings (CLIP, ResNet)
- Combined multimodal embeddings
