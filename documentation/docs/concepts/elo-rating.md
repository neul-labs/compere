# Elo Rating System

The Elo rating system, originally developed for chess, calculates relative skill levels based on head-to-head outcomes.

## How It Works

1. **Initial Rating**: All entities start at 1500 (configurable via `ELO_INITIAL_RATING`)
2. **Expected Score**: Before a comparison, we calculate each entity's probability of winning
3. **Rating Update**: After the comparison, ratings adjust based on the outcome vs expectation

## The Math

### Expected Score

The expected score (probability of winning) for entity A against entity B:

$$E_A = \frac{1}{1 + 10^{(R_B - R_A) / 400}}$$

Where:

- $E_A$ = Expected score for entity A
- $R_A$ = Current rating of entity A
- $R_B$ = Current rating of entity B

### Rating Update

After the comparison:

$$R'_A = R_A + K \times (S_A - E_A)$$

Where:

- $R'_A$ = New rating for entity A
- $K$ = K-factor (sensitivity, default 32)
- $S_A$ = Actual score (1 for win, 0 for loss, 0.5 for tie)
- $E_A$ = Expected score

## Example

Entity A (rating 1600) vs Entity B (rating 1400):

```python
# Expected scores
E_a = 1 / (1 + 10**((1400 - 1600) / 400))  # = 0.76
E_b = 1 / (1 + 10**((1600 - 1400) / 400))  # = 0.24

# If A wins (expected outcome)
R_a_new = 1600 + 32 * (1 - 0.76)  # = 1608 (+8)
R_b_new = 1400 + 32 * (0 - 0.24)  # = 1392 (-8)

# If B wins (upset!)
R_a_new = 1600 + 32 * (0 - 0.76)  # = 1576 (-24)
R_b_new = 1400 + 32 * (1 - 0.24)  # = 1424 (+24)
```

!!! info "Key Insight"
    Upsets cause larger rating changes than expected outcomes. Beating a higher-rated opponent gives more points than beating a lower-rated one.

## K-Factor

The K-factor controls rating volatility:

| K-Factor | Use Case |
|----------|----------|
| 40-50 | New systems, rapid convergence needed |
| 32 | Standard (default) |
| 16-24 | Established rankings, stability preferred |
| 10-16 | Professional leagues, slow changes |

Configure with `ELO_K_FACTOR` environment variable.

## Tie Support

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

## Rating Interpretation

| Rating Range | Interpretation |
|--------------|----------------|
| 1700+ | Exceptional |
| 1600-1700 | Excellent |
| 1500-1600 | Above average |
| 1400-1500 | Below average |
| 1300-1400 | Poor |
| < 1300 | Bottom tier |

!!! note
    These ranges are relative to your specific dataset. The actual ratings depend on the number and outcomes of comparisons.
