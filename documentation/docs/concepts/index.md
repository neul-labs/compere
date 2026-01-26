# Concepts

Understanding the algorithms that power Compere.

## Overview

Compere uses two algorithms to create an efficient ranking system:

1. **Elo Rating System** - Updates entity ratings after each comparison
2. **Multi-Armed Bandit (UCB)** - Selects optimal pairs for comparison

## Contents

- [Elo Rating System](elo-rating.md) - How ratings are calculated and updated
- [MAB Algorithm](mab-algorithm.md) - Upper Confidence Bound for pair selection
- [Entity Pairing](entity-pairing.md) - How Compere selects comparison pairs

## Algorithm Selection Guide

| Scenario | Recommended Approach |
|----------|---------------------|
| Quick ranking with few comparisons | MAB/UCB (exploration-focused) |
| Stable, established rankings | Lower K-factor (16-24) |
| New entities added frequently | Default settings (K=32, UCB with cold-start) |
| Diverse comparison coverage | Similarity matching or increase random factor |
| Statistical validity required | Random pairing (no UCB) |
