# Compere

[![CI](https://github.com/terraprompt/compere/actions/workflows/ci.yml/badge.svg)](https://github.com/terraprompt/compere/actions/workflows/ci.yml)
[![Frontend CI](https://github.com/terraprompt/compere/actions/workflows/frontend.yml/badge.svg)](https://github.com/terraprompt/compere/actions/workflows/frontend.yml)
[![PyPI version](https://badge.fury.io/py/compere.svg)](https://badge.fury.io/py/compere)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Compere is an advanced comparative rating system that leverages Multi-Armed Bandit (MAB) algorithms and Elo ratings to provide fair and efficient entity comparisons. It can be used both as a standalone web service and as a library in your Python projects.

Whether you're building a recommendation system, a product comparison platform, or any application that requires comparative rankings, Compere provides the tools to make intelligent pairwise comparisons and maintain accurate ratings.

## Key Features

### Core Algorithm Features
- **Multi-Armed Bandit (MAB) Algorithm**: Utilizes the Upper Confidence Bound (UCB) algorithm with persistent state for intelligent entity selection
- **Elo Rating System**: Implements configurable Elo ratings with K-factor tuning for accurate ranking
- **Cold-Start Problem Handling**: Prioritizes new entities to quickly integrate them into the comparison pool
- **Smart Entity Pairing**: Selects dissimilar entities for meaningful comparisons

### Production-Ready Features
- **Complete CRUD Operations**: Full Create, Read, Update, Delete support for entities with validation
- **Comparison History**: Track and query all comparisons with filtering and pagination
- **Authentication System**: JWT-based authentication with configurable security
- **Rate Limiting**: Configurable rate limiting to prevent API abuse
- **Error Handling**: Comprehensive error handling with proper rollbacks and logging
- **Input Validation**: Robust validation for all inputs with detailed error messages

### Technical Features
- **Database Agnostic**: Works with SQLite, PostgreSQL, MySQL with proper connection management
- **Environment Validation**: Startup validation of configuration and dependencies
- **Request Logging**: Configurable request/response logging for monitoring
- **Modular Architecture**: Well-organized codebase with separate modules and clear interfaces
- **RESTful API**: Comprehensive API with OpenAPI/Swagger documentation
- **Dual Usage**: Available as both a standalone web service and a Python library

## Use Cases

### As a Library
- Integrate comparative rating functionality directly into your Python applications
- Create custom comparison workflows without running a separate service
- Use in Jupyter notebooks for data analysis and research
- Build batch processing systems for large-scale comparisons

### As a Standalone Service
- Deploy as a web API for distributed applications
- Create web interfaces for human evaluators to make comparisons
- Build multi-user comparison platforms
- Integrate with frontend applications through RESTful endpoints

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLAlchemy ORM (compatible with various SQL databases)
- **Task Scheduling**: FastAPI built-in background tasks and repeat_every decorator

## Installation

Install Compere using pip:

```bash
pip install compere
```

## Usage

Compere can be used in two ways: as a library integrated into your Python projects, or as a standalone web service.

### As a Library

You can use Compere as a library in your Python projects. Here's a complete example:

```python
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from compere.modules.database import Base
from compere.modules.models import EntityCreate, ComparisonCreate
from compere.modules.entity import create_entity
from compere.modules.comparison import create_comparison
from compere.modules.rating import get_ratings
from compere.modules.mab import get_next_comparison

# Use an in-memory SQLite database for this example
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Create a database session
db = SessionLocal()

try:
    # Create some sample entities
    entity1_data = EntityCreate(
        name="Restaurant A",
        description="A fine dining restaurant with excellent service",
        image_urls=["http://example.com/restaurant_a.jpg"]
    )
    entity1 = create_entity(entity1_data, db)
    
    entity2_data = EntityCreate(
        name="Restaurant B",
        description="A casual dining spot with great ambiance",
        image_urls=["http://example.com/restaurant_b.jpg"]
    )
    entity2 = create_entity(entity2_data, db)
    
    # Perform a comparison
    comparison_data = ComparisonCreate(
        entity1_id=entity1.id,
        entity2_id=entity2.id,
        selected_entity_id=entity1.id
    )
    comparison = create_comparison(comparison_data, db)
    
    # Show updated ratings
    ratings = get_ratings(db)
    for entity in ratings:
        print(f"{entity.name}: {entity.rating:.2f}")
        
finally:
    db.close()
```

This approach is ideal when you want to integrate Compere's functionality directly into your application without running a separate service.

### As a Standalone Web Service

Run Compere as a standalone web service using the CLI:

```bash
compere --host 127.0.0.1 --port 8000
```

For development with auto-reload:

```bash
compere --host 127.0.0.1 --port 8000 --reload
```

Once running, you can access:
- The API documentation at `http://localhost:8000/docs`
- The main application endpoints for managing entities, comparisons, and ratings

### Database Configuration

Compere supports any SQL database backend. By default, it uses SQLite.

#### For Library Usage
When using Compere as a library, you can configure the database directly in your code:

```python
# For PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

# For MySQL
SQLALCHEMY_DATABASE_URL = "mysql://user:password@localhost/dbname"

# For SQLite (default)
SQLALCHEMY_DATABASE_URL = "sqlite:///./compere.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
```

#### For Standalone Service
When running Compere as a standalone service, set the `DATABASE_URL` environment variable:

```bash
# For PostgreSQL
export DATABASE_URL=postgresql://user:password@localhost/dbname

# For MySQL
export DATABASE_URL=mysql://user:password@localhost/dbname

# For SQLite (default)
export DATABASE_URL=sqlite:///./compere.db
```

### API Endpoints

When running as a standalone service, Compere provides the following RESTful API endpoints:

#### Entity Management
- `POST /entities/`: Create a new entity
- `GET /entities/`: List entities with search and pagination
- `GET /entities/{entity_id}`: Get an entity by ID
- `PUT /entities/{entity_id}`: Update an existing entity
- `DELETE /entities/{entity_id}`: Delete an entity

#### Comparison Management
- `POST /comparisons/`: Create a new comparison
- `GET /comparisons/`: List comparisons with filtering and pagination
- `GET /comparisons/{comparison_id}`: Get a specific comparison by ID
- `GET /comparisons/next`: Get the next pair of entities to compare

#### Rating System
- `GET /ratings`: Get all entities ordered by rating
- `GET /similar_entities`: Get dissimilar entities for comparison (renamed for backward compatibility)
- `GET /dissimilar_entities`: Get dissimilar entities for meaningful comparisons

#### Multi-Armed Bandit
- `GET /mab/next_comparison`: Get the next comparison from the MAB algorithm
- `POST /mab/update`: Update MAB state based on comparison result

#### Authentication (when enabled)
- `POST /auth/token`: Login to get JWT access token
- `GET /auth/users/me`: Get current user information

#### Configuration & Environment Variables

Compere supports extensive configuration through environment variables:

```bash
# Database Configuration
export DATABASE_URL=sqlite:///./compere.db  # SQLite (default)
export DATABASE_URL=postgresql://user:pass@localhost/compere  # PostgreSQL
export DATABASE_URL=mysql://user:pass@localhost/compere  # MySQL

# Elo Rating Configuration
export ELO_K_FACTOR=32.0  # Rating sensitivity (default: 32.0)

# Authentication Configuration
export AUTH_ENABLED=true  # Enable authentication (default: false)
export SECRET_KEY=your-secret-key-here  # JWT secret key

# Rate Limiting Configuration
export RATE_LIMIT_ENABLED=true  # Enable rate limiting (default: false)
export RATE_LIMIT_REQUESTS=100  # Requests per window (default: 100)
export RATE_LIMIT_WINDOW=60  # Window in seconds (default: 60)

# Logging Configuration
export LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
export LOG_REQUESTS=true  # Log HTTP requests (default: true)
export ENVIRONMENT=production  # development, staging, production
```

For a complete list of endpoints and their usage, visit the Swagger UI at `http://localhost:8000/docs` when the application is running.

### Making a Comparison

When using the standalone service, you can make comparisons through the API:

1. Create entities:
   ```bash
   POST /entities/
   {
     "name": "Restaurant A",
     "description": "A fine dining restaurant",
     "image_urls": ["http://example.com/a.jpg"]
   }
   ```

2. Get the next pair of entities to compare:
   ```bash
   GET /comparisons/next
   ```

3. Submit a comparison:
   ```bash
   POST /comparisons/
   {
     "entity1_id": 1,
     "entity2_id": 2,
     "selected_entity_id": 1
   }
   ```

4. The system will automatically update the MAB state and Elo ratings based on the comparison.

When using Compere as a library, you can make comparisons directly through function calls as shown in the library usage example above.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/compere.git
   cd compere
   ```

2. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install dependencies:
   ```bash
   uv sync --all-extras
   ```

4. Set up environment variables (optional):
   Create a `.env` file in the root directory and add the following:
   ```
   DATABASE_URL=sqlite:///./compere.db
   ```

5. Run the application as a standalone service:
   ```bash
   uv run compere --reload
   ```

The API will be available at `http://localhost:8000`.

### Using as a Library

To use Compere as a library in your own projects, simply install it from PyPI:
```bash
pip install compere
```

Then import and use the modules directly in your Python code:
```python
from compere.modules.entity import create_entity
from compere.modules.comparison import create_comparison
from compere.modules.rating import get_ratings
```

## Running Tests

To run the tests, use pytest:

```bash
# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/test_compere.py

# Run tests with coverage
uv run pytest --cov=compere
```

## Contributing

Contributions to Compere are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-branch-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The Elo rating system, developed by Arpad Elo
- The Multi-Armed Bandit algorithm and its applications in decision making
- The FastAPI framework and its community

For any questions or support, please open an issue in the GitHub repository.