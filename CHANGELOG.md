# Changelog

## [0.2.0] - 2024-12-XX

### 🚀 Major Features Added
- **MAB State Persistence**: Multi-Armed Bandit algorithm now persists state between requests via database storage
- **Complete CRUD Operations**: Full Create, Read, Update, Delete support for entities
- **Comparison History**: Track and query comparison history with filtering
- **Authentication System**: JWT-based authentication with configurable security
- **Rate Limiting**: Configurable rate limiting middleware to prevent abuse
- **Environment Validation**: Comprehensive validation of configuration and dependencies

### 🔧 Critical Fixes
- **Fixed MAB State Bug**: UCB algorithm now properly maintains learning state
- **Fixed Image URL Serialization**: Proper JSON handling for image URL arrays
- **Fixed Similarity Logic**: Now correctly selects dissimilar entities for meaningful comparisons
- **Fixed Database Naming**: Consistent database naming (compere.db)
- **Added Missing Imports**: HTTPException properly imported in MAB module

### 📊 API Improvements
- **New Endpoints**:
  - `GET /entities/` - List entities with search and pagination
  - `PUT /entities/{id}` - Update existing entities
  - `DELETE /entities/{id}` - Delete entities
  - `GET /comparisons/` - List comparisons with filtering
  - `GET /comparisons/{id}` - Get specific comparison
  - `POST /auth/token` - Authentication endpoint
  - `GET /auth/users/me` - Current user info
  - `GET /dissimilar_entities` - Get dissimilar entities

### 🛡️ Security & Production Features
- **Input Validation**: Comprehensive validation for all entity fields
- **Error Handling**: Robust error handling with proper rollbacks
- **Request Logging**: Configurable request/response logging
- **CORS Support**: Proper CORS configuration
- **Environment Variables**: Support for production configuration

### ⚙️ Configuration Options
- `DATABASE_URL` - Database connection string
- `ELO_K_FACTOR` - Configurable Elo rating sensitivity (default: 32.0)
- `AUTH_ENABLED` - Enable/disable authentication (default: false)
- `SECRET_KEY` - JWT secret key (required if auth enabled)
- `RATE_LIMIT_ENABLED` - Enable rate limiting (default: false)
- `RATE_LIMIT_REQUESTS` - Requests per window (default: 100)
- `RATE_LIMIT_WINDOW` - Rate limit window in seconds (default: 60)
- `LOG_LEVEL` - Logging level (default: INFO)
- `ENVIRONMENT` - Environment type (development/staging/production)

### 🧪 Testing
- **Comprehensive Test Suite**: Unit and integration tests for all components
- **Database Testing**: Isolated database testing with in-memory SQLite
- **API Testing**: Complete FastAPI endpoint testing
- **Validation Testing**: Input validation and error handling tests

### 📝 Documentation
- Updated README with all new features
- Added configuration documentation
- Improved API examples
- Added troubleshooting guide

### 🔄 Breaking Changes
- Removed unused `user_id` parameter from `/comparisons/next` endpoint
- Changed similarity endpoint behavior to return dissimilar entities
- Modified database schema to include MAB state table

### 🐛 Bug Fixes
- Fixed entity creation with proper JSON serialization
- Improved error messages and status codes
- Fixed database connection handling
- Resolved middleware configuration issues

## [0.1.0] - Initial Release
- Basic entity and comparison management
- Elo rating system
- Multi-Armed Bandit algorithm
- FastAPI web service
- SQLite database support