# Multi-Armed Bandit (UCB)

The UCB (Upper Confidence Bound) algorithm solves the exploration-exploitation dilemma: should we compare well-known entities or explore less-compared ones?

## The Problem

With N entities, there are N*(N-1)/2 possible pairs. We want to find the best rankings with minimal comparisons by intelligently selecting which pairs to compare next.

## How UCB Works

For each entity, UCB calculates a score that balances:

1. **Exploitation**: Entities with uncertain ratings (might be underrated)
2. **Exploration**: Entities with few comparisons (need more data)

### UCB Score Formula

$$UCB_i = \bar{X}_i + c \times \sqrt{\frac{\ln(n)}{n_i}}$$

Where:

- $\bar{X}_i$ = Average reward (win rate) for entity i
- $c$ = Exploration constant (typically $\sqrt{2}$ ≈ 1.414)
- $n$ = Total comparisons
- $n_i$ = Comparisons involving entity i

## Entity Selection

1. Calculate UCB score for each entity
2. Select the entity with highest UCB score
3. Pair with the entity that maximizes information gain
4. After comparison, update statistics

## Cold-Start Handling

New entities have $n_i = 0$, which would make UCB undefined. Compere handles this by:

1. Assigning infinite UCB to entities with zero comparisons
2. Ensuring new entities are prioritized for their first comparison

```python
if state.count == 0:
    ucb_scores[state.entity_id] = float('inf')  # Prioritize exploration
else:
    ucb_scores[state.entity_id] = state.value + c * sqrt(2 * log(n) / n_i)
```

## Example

```
Entity A: 10 comparisons, 7 wins (70% win rate)
Entity B: 2 comparisons, 1 win (50% win rate)
Entity C: 0 comparisons

Total comparisons: 12

UCB_A = 0.70 + 1.414 * sqrt(ln(12) / 10) = 0.70 + 0.70 = 1.40
UCB_B = 0.50 + 1.414 * sqrt(ln(12) / 2)  = 0.50 + 1.57 = 2.07
UCB_C = ∞ (prioritized, no comparisons yet)
```

Entity C would be selected first (cold-start). If C is excluded, Entity B is selected despite lower win rate because of higher uncertainty.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `UCB_EXPLORATION_CONSTANT` | `1.414` | Controls exploration vs exploitation |
| `UCB_UNEXPLORED_WEIGHT` | `1000.0` | Weight for entities with 0 comparisons |

## Weighted Random Selection

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

## Convergence

With random pairing, ranking N entities requires O(N²) comparisons. UCB reduces this to roughly O(N log N) by:

1. Quickly identifying top/bottom performers
2. Focusing comparisons on uncertain middle rankings
3. Avoiding redundant comparisons between established entities

## When to Use UCB

| Scenario | Use UCB? |
|----------|----------|
| Minimizing total comparisons | Yes |
| Rapid ranking convergence | Yes |
| New entities added frequently | Yes |
| Statistical validity required | No (use random) |
| Unbiased sampling needed | No (use random) |
