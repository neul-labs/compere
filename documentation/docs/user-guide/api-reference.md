# API Reference

Full documentation for Compere's REST API endpoints.

**Base URL**: `http://localhost:8090` (default)

**Interactive docs**: `http://localhost:8090/docs` (Swagger UI)

## Health Check

### Basic Health Check

```http
GET /health
```

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "0.1.0"
}
```

### Readiness Check

```http
GET /health/ready
```

Verifies database connectivity.

**Response**: `200 OK`
```json
{
  "status": "ready",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response**: `503 Service Unavailable` (if database is down)

## Entities

Entities are the items being compared and ranked.

### Create Entity

```http
POST /entities/
```

**Request Body:**
```json
{
  "name": "Restaurant A",
  "description": "Fine dining establishment",
  "image_urls": ["https://example.com/image.jpg"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Entity name (max 200 chars) |
| `description` | string | No | Description (max 1000 chars) |
| `image_urls` | array | No | List of image URLs (max 10) |

**Response**: `200 OK`
```json
{
  "id": 1,
  "name": "Restaurant A",
  "description": "Fine dining establishment",
  "image_urls": ["https://example.com/image.jpg"],
  "rating": 1500.0
}
```

### List Entities

```http
GET /entities/
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 100 | Max results (1-1000) |
| `search` | string | null | Search by name/description |

**Response**: `200 OK`
```json
[
  {"id": 1, "name": "Restaurant A", "rating": 1520.0, ...},
  {"id": 2, "name": "Restaurant B", "rating": 1480.0, ...}
]
```

### Get Entity

```http
GET /entities/{entity_id}
```

**Response**: `200 OK` or `404 Not Found`

### Update Entity

```http
PUT /entities/{entity_id}
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "image_urls": ["https://example.com/new.jpg"]
}
```

All fields are optional. Only provided fields are updated.

### Delete Entity

```http
DELETE /entities/{entity_id}
```

**Response**: `200 OK`
```json
{"message": "Entity deleted successfully"}
```

## Comparisons

Record and retrieve pairwise comparisons.

### Create Comparison

```http
POST /comparisons/
```

**Request Body:**
```json
{
  "entity1_id": 1,
  "entity2_id": 2,
  "selected_entity_id": 1
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entity1_id` | int | Yes | First entity ID |
| `entity2_id` | int | Yes | Second entity ID |
| `selected_entity_id` | int | Yes | Winner's ID (must be entity1 or entity2) |

This endpoint:

1. Records the comparison
2. Updates Elo ratings for both entities
3. Updates MAB state

**Response**: `200 OK`
```json
{
  "id": 1,
  "entity1_id": 1,
  "entity2_id": 2,
  "selected_entity_id": 1,
  "created_at": "2024-01-15T10:35:00Z"
}
```

### List Comparisons

```http
GET /comparisons/
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 100 | Max results |
| `entity_id` | int | null | Filter by entity |

### Get Comparison

```http
GET /comparisons/{comparison_id}
```

### Get Next Comparison (Similarity-based)

```http
GET /comparisons/next
```

Returns a pair of dissimilar entities for comparison.

## Ratings

### Get Leaderboard

```http
GET /ratings
```

Returns all entities sorted by rating (highest first).

**Response**: `200 OK`
```json
[
  {"id": 3, "name": "Top Rated", "rating": 1650.0, ...},
  {"id": 1, "name": "Second Place", "rating": 1520.0, ...},
  {"id": 2, "name": "Third Place", "rating": 1480.0, ...}
]
```

## Multi-Armed Bandit

### Get Next Comparison (MAB)

```http
GET /mab/next_comparison
```

Uses the UCB algorithm to select the optimal pair for comparison. Prioritizes:

- New entities (cold-start handling)
- High-uncertainty pairs
- Exploration/exploitation balance

**Response**: `200 OK`
```json
{
  "entity1": {"id": 1, "name": "Entity A", "rating": 1500.0, ...},
  "entity2": {"id": 2, "name": "Entity B", "rating": 1500.0, ...}
}
```

**Error**: `400 Bad Request` if fewer than 2 entities exist.

### Update MAB State

```http
POST /mab/update?comparison_id={id}
```

Manually update MAB state (usually handled automatically by `POST /comparisons/`).

## Similarity

### Get Dissimilar Entities

```http
GET /dissimilar_entities
```

Returns a pair of entities that are dissimilar (for meaningful comparisons).

## Authentication

When `AUTH_ENABLED=true`, these endpoints are available.

### Login

```http
POST /auth/token?username={username}&password={password}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Get Current User

```http
GET /auth/users/me
```

**Headers:**
```
Authorization: Bearer eyJ...
```

### Create User

```http
POST /auth/users/
```

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "full_name": "New User",
  "password": "securepassword"
}
```

!!! note
    The first user created is automatically a superuser.

## Error Responses

All errors return JSON:

```json
{
  "detail": "Error message here"
}
```

| Status | Meaning |
|--------|---------|
| `400` | Bad request (invalid input) |
| `401` | Unauthorized (auth required) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Resource not found |
| `422` | Validation error |
| `429` | Rate limit exceeded |
| `500` | Server error |
| `503` | Service unavailable |
