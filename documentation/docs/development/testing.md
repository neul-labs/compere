# Testing

Running and writing tests for Compere.

## Running Tests

### Basic Usage

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_api.py

# Run tests matching pattern
uv run pytest -k "test_entity"
```

### Coverage Reports

```bash
# Run with coverage
uv run pytest --cov=compere

# Generate HTML report
uv run pytest --cov=compere --cov-report=html

# View report
open htmlcov/index.html
```

### Test Options

```bash
# Stop on first failure
uv run pytest -x

# Show local variables on failure
uv run pytest -l

# Run previously failed tests
uv run pytest --lf

# Parallel execution
uv run pytest -n auto
```

## Test Structure

Tests are located in `/tests/`:

```
tests/
├── __init__.py
├── test_api.py          # API endpoint tests
├── test_auth.py         # Authentication tests
├── test_cli.py          # CLI tests
├── test_comparison.py   # Comparison logic tests
├── test_compere.py      # Core functionality tests
├── test_config.py       # Configuration tests
├── test_entity.py       # Entity CRUD tests
└── test_middleware.py   # Middleware tests
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from fastapi.testclient import TestClient
from compere.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Using Fixtures

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from compere.modules.database import Base


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_entity(db_session):
    """Test entity creation."""
    from compere.modules.entity import create_entity
    from compere.modules.models import EntityCreate

    entity = create_entity(
        EntityCreate(name="Test", description="Test entity", image_urls=[]),
        db_session
    )
    assert entity.name == "Test"
    assert entity.rating == 1500.0
```

### Testing API Endpoints

```python
from fastapi.testclient import TestClient
from compere.main import app

client = TestClient(app)


def test_create_entity_api():
    """Test entity creation via API."""
    response = client.post(
        "/entities/",
        json={
            "name": "Test Entity",
            "description": "A test",
            "image_urls": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Entity"
    assert data["rating"] == 1500.0


def test_create_entity_validation():
    """Test entity validation."""
    response = client.post(
        "/entities/",
        json={
            "name": "",  # Empty name should fail
            "description": "Test",
            "image_urls": []
        }
    )
    assert response.status_code == 422
```

### Testing Authentication

```python
def test_auth_required():
    """Test that protected endpoints require authentication."""
    response = client.get("/auth/users/me")
    assert response.status_code == 401


def test_login_success(db_session):
    """Test successful login."""
    # Create user first
    from compere.modules.auth import create_user
    from compere.modules.models import UserCreate

    create_user(
        db_session,
        UserCreate(username="testuser", password="testpass"),
        is_superuser=True
    )

    response = client.post(
        "/auth/token",
        params={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Mocking

```python
from unittest.mock import patch


def test_with_mock():
    """Test with mocked dependency."""
    with patch("compere.modules.config.get_config") as mock_config:
        mock_config.return_value = {
            "environment": "test",
            "elo_k_factor": 32.0
        }
        # Test code that uses config
```

## Test Coverage Goals

| Module | Target Coverage |
|--------|-----------------|
| `entity.py` | 90%+ |
| `comparison.py` | 90%+ |
| `auth.py` | 85%+ |
| `mab.py` | 80%+ |
| `config.py` | 85%+ |
| Overall | 80%+ |

## CI Integration

Tests run automatically on:

- Push to `main` branch
- Pull requests

GitHub Actions configuration in `.github/workflows/ci.yml` runs:

1. Lint check (`ruff check`)
2. Test suite (`pytest`)
3. Coverage report (uploaded to Codecov)
