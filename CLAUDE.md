# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Compere is a dual-purpose comparative rating system that leverages Multi-Armed Bandit (MAB) algorithms and Elo ratings. It operates both as a standalone web service (FastAPI) and as a Python library. The system includes a Vue.js frontend UI for interactive demonstrations and simulations.

## Architecture

### Backend Structure
- **FastAPI Application**: `compere/main.py` - Main application entry point with middleware setup
- **Modular Design**: `compere/modules/` - Each module handles specific functionality:
  - `models.py` - SQLAlchemy ORM models (Entity, Comparison, MABState) and Pydantic schemas
  - `database.py` - Database connection and session management
  - `entity.py` - CRUD operations for entities
  - `comparison.py` - Comparison management and creation
  - `rating.py` - Elo rating calculations and leaderboards
  - `mab.py` - Multi-Armed Bandit algorithm with Upper Confidence Bound (UCB)
  - `similarity.py` - Entity similarity calculations for intelligent pairing
  - `auth.py` - JWT authentication system (optional)
  - `middleware.py` - Rate limiting and request logging middleware
  - `config.py` - Environment validation and configuration management

### Frontend Structure
- **Vue.js 3 Application**: `compere-ui/` - Interactive simulation interface
- **State Management**: Pinia stores for entities, comparisons, and authentication
- **Simulation Scenarios**: Pre-built datasets (restaurants, gamers, movies, products)
- **API Integration**: Axios-based client with automatic authentication

### Key Algorithms
1. **Elo Rating System**: Dynamic rating updates based on pairwise comparisons
2. **Multi-Armed Bandit (UCB)**: Intelligent entity selection with exploration/exploitation balance
3. **Similarity Matching**: Ensures meaningful comparisons by selecting dissimilar entities

## Common Commands

### Backend Development (Poetry)
```bash
# Start development server on port 8090
poetry run compere --reload

# Start with custom port
poetry run compere --host 127.0.0.1 --port 8090 --reload

# Install dependencies
poetry install

# Run tests (when available)
poetry run pytest

# Access CLI help
poetry run compere --help
```

### Frontend Development
```bash
# Navigate to UI directory
cd compere-ui

# Install dependencies
npm install

# Start development server (auto-assigns port, usually 3000/3001)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Database Management
- **Default**: SQLite at `./compere.db` (auto-created)
- **Configuration**: Set `DATABASE_URL` environment variable
- **Reset**: Delete `compere.db` file and restart server

## Key Configuration

### Environment Variables
- `DATABASE_URL` - Database connection string (default: sqlite:///./compere.db)
- `ELO_K_FACTOR` - Rating sensitivity (default: 32.0)
- `AUTH_ENABLED` - Enable JWT authentication (default: false)
- `SECRET_KEY` - JWT secret (required if AUTH_ENABLED=true)
- `RATE_LIMIT_ENABLED` - Enable rate limiting (default: false)
- `LOG_LEVEL` - Logging level (default: INFO)
- `ENVIRONMENT` - Environment type (development/staging/production)

### Frontend Configuration
- `.env` file with `VITE_API_BASE_URL=http://localhost:8090`
- Default API connection to backend on port 8090

## Critical Architecture Details

### Database Model Relationships
- **Entity**: Core entity with name, description, image_urls (JSON), and Elo rating
- **Comparison**: Records pairwise comparisons with winner selection
- **MABState**: Persistent Multi-Armed Bandit state per entity (UCB algorithm)

### MAB Algorithm Flow
1. `get_next_comparison()` uses UCB to select optimal entity pairs
2. Prioritizes new entities (cold-start handling)
3. Balances exploration vs exploitation with confidence intervals
4. State persists in database for consistent learning

### API Architecture
- **Modular Routers**: Each module defines its own FastAPI router
- **Dependency Injection**: Database sessions via FastAPI dependencies
- **Middleware Stack**: CORS → Rate Limiting → Logging → Authentication
- **Error Handling**: Comprehensive with proper HTTP status codes

### Frontend-Backend Integration
- **API Client**: `compere-ui/src/services/api.js` - Centralized Axios client
- **State Management**: Pinia stores mirror backend entities
- **Simulation Engine**: `compere-ui/src/utils/simulation.js` - Automated comparison generation
- **Real-time Updates**: Immediate rating updates after comparisons

## Development Workflow

1. **Backend Changes**: Modify modules in `compere/modules/`, server auto-reloads with `--reload`
2. **Frontend Changes**: Modify Vue components in `compere-ui/src/`, Vite provides HMR
3. **Database Schema Changes**: Update `models.py`, delete `compere.db`, restart server
4. **New Scenarios**: Add to `compere-ui/src/utils/simulation.js`

## Testing Strategy

- Backend uses pytest framework (dependencies configured in pyproject.toml)
- No existing test files - tests need to be created in project root or `tests/` directory
- Frontend testing not yet configured

## Important Notes

- **Port Configuration**: Backend defaults to 8090, frontend auto-assigns (usually 3001)
- **Database Auto-Creation**: Tables created automatically on startup via SQLAlchemy
- **Model Registration**: Models must be imported in `main.py` to register with SQLAlchemy Base
- **CORS**: Configured for development with allow_origins=["*"]
- **Simulation Data**: Rich datasets with Unsplash images for realistic demonstrations

## Common Issues

- **"no such table" errors**: Models not imported in main.py, or database needs recreation
- **Port conflicts**: Use `lsof -ti:PORT | xargs kill -9` to clear ports
- **Frontend API connection**: Ensure `.env` file exists with correct `VITE_API_BASE_URL`
- **Missing dependencies**: Run `poetry install` for backend, `npm install` for frontend