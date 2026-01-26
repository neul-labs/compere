# Installation

## Package Installation

### Using uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager written in Rust.

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

For development with all dependencies:

```bash
uv sync --all-extras
```

## Verify Installation

```bash
# Check CLI is available
compere --help

# Or with uv
uv run compere --help
```

## Demo UI Installation (Optional)

The Vue.js frontend provides an interactive interface for demonstrations.

```bash
cd compere-ui
npm install
```

## Dependencies

Compere automatically installs these dependencies:

| Package | Purpose |
|---------|---------|
| FastAPI | Web framework |
| SQLAlchemy | Database ORM |
| uvicorn | ASGI server |
| python-jose | JWT handling |
| passlib | Password hashing |
| numpy | Numerical operations |
| scikit-learn | Similarity calculations |

## System Requirements

- **Python**: 3.11 or higher
- **Memory**: 256MB minimum
- **Disk**: 50MB for installation
- **Database**: SQLite (default), PostgreSQL, or MySQL
