# Compere

**A comparative rating system using Multi-Armed Bandit algorithms and Elo ratings.**

Compere is a dual-purpose system that operates both as a standalone web service (FastAPI) and as a Python library. It combines the proven Elo rating system with intelligent Multi-Armed Bandit (MAB) algorithms to efficiently rank entities through pairwise comparisons.

## Features

- **Elo Rating System** - Dynamic rating updates based on pairwise comparisons
- **Multi-Armed Bandit (UCB)** - Intelligent entity selection with exploration/exploitation balance
- **REST API** - Full-featured FastAPI backend with OpenAPI documentation
- **Python Library** - Direct integration without running a separate server
- **Vue.js Demo UI** - Interactive interface for simulations and demonstrations
- **Database Flexibility** - Supports SQLite, PostgreSQL, and MySQL
- **Production Ready** - Docker support, rate limiting, authentication, and more

## Quick Start

=== "Using uv (Recommended)"

    ```bash
    uv add compere
    uv run compere --port 8090 --reload
    ```

=== "Using pip"

    ```bash
    pip install compere
    compere --port 8090 --reload
    ```

=== "From Source"

    ```bash
    git clone https://github.com/terraprompt/compere.git
    cd compere
    uv sync
    uv run compere --port 8090 --reload
    ```

Once running, visit `http://localhost:8090/docs` for the interactive API documentation.

## Use Cases

| Scenario | Description |
|----------|-------------|
| **Product Rankings** | Compare products based on user preferences |
| **Content Moderation** | Rank content quality through human evaluation |
| **A/B Testing** | Compare variations using pairwise judgments |
| **Recommendation Systems** | Build preference models from comparisons |
| **Survey Research** | Collect comparative preference data |
| **Gaming/Esports** | Maintain player or team rankings |

## How It Works

```mermaid
graph LR
    A[Get Next Pair] --> B[UCB Algorithm]
    B --> C[User Compares]
    C --> D[Update Elo Ratings]
    D --> E[Update MAB State]
    E --> A
```

1. **UCB Algorithm** selects the optimal pair for comparison
2. **User/evaluator** makes a comparison decision
3. **Elo ratings** are updated based on the outcome
4. **MAB state** is updated to improve future pair selection
5. Repeat until ratings converge

## Documentation

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting Started**

    ---

    Install Compere and run your first comparison

    [:octicons-arrow-right-24: Installation](getting-started/installation.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete REST API endpoint documentation

    [:octicons-arrow-right-24: API Reference](user-guide/api-reference.md)

-   :material-language-python:{ .lg .middle } **Library Usage**

    ---

    Use Compere as a Python library

    [:octicons-arrow-right-24: Library Usage](user-guide/library-usage.md)

-   :material-cog:{ .lg .middle } **Configuration**

    ---

    Environment variables and options

    [:octicons-arrow-right-24: Configuration](user-guide/configuration.md)

-   :material-chart-line:{ .lg .middle } **Algorithms**

    ---

    How Elo and MAB algorithms work

    [:octicons-arrow-right-24: Concepts](concepts/index.md)

-   :material-docker:{ .lg .middle } **Deployment**

    ---

    Docker, production setup, and troubleshooting

    [:octicons-arrow-right-24: Deployment](deployment/index.md)

</div>

## License

MIT License - Copyright (c) 2025 Skelf Research
