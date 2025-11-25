# Algorithms

Compere uses two algorithms to create an efficient ranking system:
1. **Elo Rating System** - Updates entity ratings after each comparison
2. **Multi-Armed Bandit (UCB)** - Selects optimal pairs for comparison

## Elo Rating System

The Elo rating system, originally developed for chess, calculates relative skill levels based on head-to-head outcomes.

### How It Works

1. **Initial Rating**: All entities start at 1500 (configurable)
2. **Expected Score**: Before a comparison, we calculate each entity's probability of winning
3. **Rating Update**: After the comparison, ratings adjust based on the outcome vs expectation

### The Math

**Expected Score:**
```
E_a = 1 / (1 + 10^((R_b - R_a) / 400))
```

Where:
- `E_a` = Expected score for entity A (probability of winning)
- `R_a` = Current rating of entity A
- `R_b` = Current rating of entity B

**Rating Update:**
```
R'_a = R_a + K * (S_a - E_a)
```

Where:
- `R'_a` = New rating for entity A
- `K` = K-factor (sensitivity, default 32)
- `S_a` = Actual score (1 for win, 0 for loss)
- `E_a` = Expected score

### Example

Entity A (rating 1600) vs Entity B (rating 1400):

```python
# Expected scores
E_a = 1 / (1 + 10**((1400 - 1600) / 400))  # = 0.76
E_b = 1 / (1 + 10**((1600 - 1400) / 400))  # = 0.24

# If A wins (expected outcome)
R'_a = 1600 + 32 * (1 - 0.76)  # = 1608 (+8)
R'_b = 1400 + 32 * (0 - 0.24)  # = 1392 (-8)

# If B wins (upset!)
R'_a = 1600 + 32 * (0 - 0.76)  # = 1576 (-24)
R'_b = 1400 + 32 * (1 - 0.24)  # = 1424 (+24)
```

Upsets cause larger rating changes than expected outcomes.

### K-Factor

The K-factor controls rating volatility:

| K-Factor | Use Case |
|----------|----------|
| 40-50 | New systems, rapid convergence needed |
| 32 | Standard (default) |
| 16-24 | Established rankings, stability preferred |
| 10-16 | Professional leagues, slow changes |

Configure with `ELO_K_FACTOR` environment variable.

## Multi-Armed Bandit (UCB)

The UCB (Upper Confidence Bound) algorithm solves the exploration-exploitation dilemma: should we compare well-known entities or explore less-compared ones?

### The Problem

With N entities, there are N*(N-1)/2 possible pairs. We want to find the best rankings with minimal comparisons by intelligently selecting which pairs to compare next.

### How UCB Works

For each entity, UCB calculates a score that balances:
1. **Exploitation**: Entities with uncertain ratings (might be underrated)
2. **Exploration**: Entities with few comparisons (need more data)

**UCB Score:**
```
UCB_i = X_i + c * sqrt(ln(n) / n_i)
```

Where:
- `X_i` = Average reward (win rate) for entity i
- `c` = Exploration constant (typically sqrt(2))
- `n` = Total comparisons
- `n_i` = Comparisons involving entity i

### Entity Selection

1. Calculate UCB score for each entity
2. Select the entity with highest UCB score
3. Pair with the entity that maximizes information gain
4. After comparison, update statistics

### Cold-Start Handling

New entities have `n_i = 0`, which would make UCB undefined. Compere handles this by:

1. Prioritizing entities with zero comparisons
2. Using a small initial pull count to avoid division by zero
3. Ensuring new entities quickly enter the comparison pool

### Example

```
Entity A: 10 comparisons, 7 wins (70% win rate)
Entity B: 2 comparisons, 1 win (50% win rate)
Entity C: 0 comparisons

Total comparisons: 12

UCB_A = 0.70 + sqrt(2) * sqrt(ln(12) / 10) = 0.70 + 0.70 = 1.40
UCB_B = 0.50 + sqrt(2) * sqrt(ln(12) / 2)  = 0.50 + 1.57 = 2.07
UCB_C = prioritized (no comparisons yet)
```

Entity C would be selected first (cold-start). If C is excluded, Entity B is selected despite lower win rate because of higher uncertainty.

## Compere's Implementation Tweaks

Compere extends the standard algorithms with several practical improvements.

### Elo Tweaks

**1. Tie Support**

Standard Elo only handles win/loss. Compere supports ties:

```python
if winner_id == entity1.id:
    score_a, score_b = 1, 0      # Entity 1 wins
elif winner_id == entity2.id:
    score_a, score_b = 0, 1      # Entity 2 wins
else:
    score_a, score_b = 0.5, 0.5  # Tie
```

Ties result in smaller rating adjustments, useful when preferences are genuinely equal.

**2. Environment-Configurable K-Factor**

K-factor is configurable at runtime via `ELO_K_FACTOR` environment variable, allowing tuning without code changes.

### UCB Tweaks

**1. Infinite UCB for Unexplored Entities**

Entities with zero comparisons receive infinite UCB score:

```python
if state.count == 0:
    ucb_scores[state.entity_id] = float('inf')  # Prioritize exploration
else:
    ucb_scores[state.entity_id] = state.value + sqrt(2 * log(total_count) / state.count)
```

This guarantees new entities are compared immediately (cold-start handling).

**2. Weighted Random Selection (Not Greedy)**

Standard UCB greedily selects the highest-scoring arm. Compere uses weighted random selection:

```python
weights = []
for entity in entities:
    score = ucb_scores.get(entity.id, 0)
    if score == float('inf'):
        weights.append(1000.0)  # High weight for unexplored
    else:
        weights.append(max(score, 0.1))

entity1 = random.choices(entities, weights=weights, k=1)[0]
```

This adds variety while still favoring high-UCB entities, preventing repetitive comparisons.

**3. Multi-Factor Pairing for Second Entity**

After selecting the first entity, the second is chosen using a composite score:

| Factor | Weight | Purpose |
|--------|--------|---------|
| UCB Score | 30% | Exploration value |
| Rating Similarity | 40% | Informative comparisons |
| Random | 30% | Variety |

```python
for entity in remaining_entities:
    score = 0
    score += ucb_scores.get(entity.id, 0) * 0.3          # Exploration

    rating_diff = abs(entity1.rating - entity.rating)
    if rating_diff < 200:
        score += (200 - rating_diff) / 200 * 0.4        # Similarity bonus

    score += random.random() * 0.3                       # Variety
```

**Rating similarity** preference (within 200 points) creates more informative comparisons—comparing a 1600 vs 1580 rated entity is more useful than 1600 vs 1200.

**4. Recent Comparison Exclusion**

Avoids re-comparing the same pairs repeatedly:

```python
recent_comparisons = db.query(Comparison).filter(
    (Comparison.entity1_id == entity1.id) | (Comparison.entity2_id == entity1.id)
).order_by(Comparison.created_at.desc()).limit(5).all()

# Exclude recently compared opponents
non_recent = [e for e in remaining if e.id not in recent_opponent_ids]
```

The last 5 opponents are excluded (when alternatives exist), ensuring broader coverage.

**5. Tie Reward Handling**

When a comparison results in a tie, both entities receive 0.5 reward:

```python
if comparison.selected_entity_id == comparison.entity1_id:
    ucb.update(comparison.entity1_id, 1.0)
    ucb.update(comparison.entity2_id, 0.0)
elif comparison.selected_entity_id == comparison.entity2_id:
    ucb.update(comparison.entity1_id, 0.0)
    ucb.update(comparison.entity2_id, 1.0)
else:
    # Tie case
    ucb.update(comparison.entity1_id, 0.5)
    ucb.update(comparison.entity2_id, 0.5)
```

### Similarity Matching

The similarity endpoint (`/dissimilar_entities`) uses cosine similarity on entity embeddings:

```python
embeddings = np.array([generate_embedding(entity) for entity in entities])
similarities = cosine_similarity(embeddings)

# Find most dissimilar pair
most_dissimilar_pair = np.unravel_index(np.argmin(similarities), similarities.shape)
```

**Current implementation**: Uses placeholder random embeddings. For production, replace `generate_embedding()` with actual embeddings from:
- Text embeddings (OpenAI, Sentence Transformers)
- Image embeddings (CLIP, ResNet)
- Combined multimodal embeddings

### Algorithm Selection Guide

| Scenario | Recommended Approach |
|----------|---------------------|
| Quick ranking with few comparisons | MAB/UCB (exploration-focused) |
| Stable, established rankings | Lower K-factor (16-24) |
| New entities added frequently | Default settings (K=32, UCB with cold-start) |
| Diverse comparison coverage | Similarity matching or increase random factor |
| Statistical validity required | Random pairing (no UCB) |

## Combining Elo and UCB

Compere uses both algorithms together:

```
┌─────────────────────────────────────────────────────────┐
│                     Comparison Flow                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. UCB Algorithm selects optimal pair                   │
│     └─> GET /mab/next_comparison                         │
│                                                          │
│  2. User/evaluator makes comparison                      │
│     └─> Human preference or automated scoring            │
│                                                          │
│  3. Record comparison, update Elo ratings                │
│     └─> POST /comparisons/                               │
│                                                          │
│  4. Update UCB statistics                                │
│     └─> Automatic (pull counts, rewards)                 │
│                                                          │
│  5. Repeat until ratings converge                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Convergence

With random pairing, ranking N entities requires O(N²) comparisons. UCB reduces this to roughly O(N log N) by:

1. Quickly identifying top/bottom performers
2. Focusing comparisons on uncertain middle rankings
3. Avoiding redundant comparisons between established entities

## Similarity Matching

Compere also offers similarity-based pairing (`GET /comparisons/next`) which selects dissimilar entities. This ensures:

- Meaningful comparisons (not comparing near-identical items)
- Broader coverage of the entity space
- Useful when UCB exploration is less critical

## When to Use Each Approach

| Approach | Use When |
|----------|----------|
| MAB/UCB (`/mab/next_comparison`) | Minimizing total comparisons, rapid ranking convergence |
| Similarity (`/comparisons/next`) | Ensuring diverse comparisons, avoiding redundancy |
| Random | Unbiased sampling, statistical validity |

## References

- Elo, Arpad (1978). *The Rating of Chessplayers, Past and Present*
- Auer, P., Cesa-Bianchi, N., & Fischer, P. (2002). *Finite-time Analysis of the Multiarmed Bandit Problem*
- Jamieson, K. G., & Nowak, R. (2011). *Active Ranking using Pairwise Comparisons*
