# Development

Contributing to and developing with Compere.

## Contents

- [Contributing](contributing.md) - How to contribute to Compere
- [Testing](testing.md) - Running and writing tests
- [Architecture](architecture.md) - Understanding the codebase

## Development Setup

```bash
# Clone the repository
git clone https://github.com/terraprompt/compere.git
cd compere

# Install with dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linting
uvx ruff check .

# Start development server
uv run compere --reload
```
