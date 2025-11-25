# API Reference

Full documentation for Compere's REST API endpoints.

Base URL: `http://localhost:8090` (default)

Interactive docs: `http://localhost:8090/docs` (Swagger UI)

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
| `name` | string | Yes | Entity name (unique) |
| `description` | string | No | Description text |
| `image_urls` | array | No | List of image URLs |

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Restaurant A",
  "description": "Fine dining establishment",
  "image_urls": ["https://example.com/image.jpg"],
  "rating": 1500.0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
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
| `search` | string | null | Search by name |

**Response:** `200 OK`
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

**Response:** `200 OK` or `404 Not Found`

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

**Response:** `200 OK`
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

**Response:** `201 Created`
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

**Response:** `200 OK`
```json
{
  "entity1": {"id": 1, "name": "Entity A", ...},
  "entity2": {"id": 2, "name": "Entity B", ...}
}
```

## Ratings

### Get Leaderboard

```http
GET /ratings
```

Returns all entities sorted by rating (highest first).

**Response:** `200 OK`
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

**Response:** `200 OK`
```json
{
  "entity1": {"id": 1, "name": "Entity A", "rating": 1500.0, ...},
  "entity2": {"id": 2, "name": "Entity B", "rating": 1500.0, ...}
}
```

**Error:** `400 Bad Request` if fewer than 2 entities exist.

### Update MAB State

```http
POST /mab/update
```

Manually update MAB state (usually handled automatically by `POST /comparisons/`).

**Request Body:**
```json
{
  "entity_id": 1,
  "reward": 1.0
}
```

## Similarity

### Get Dissimilar Entities

```http
GET /dissimilar_entities
```

Returns a pair of entities that are dissimilar (for meaningful comparisons).

**Response:** `200 OK`
```json
{
  "entity1": {"id": 1, ...},
  "entity2": {"id": 2, ...}
}
```

## Authentication

When `AUTH_ENABLED=true`, these endpoints are available.

### Login

```http
POST /auth/token
```

**Request Body:** (form data)
```
username=admin&password=secret
```

**Response:** `200 OK`
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
| `404` | Resource not found |
| `422` | Validation error |
| `429` | Rate limit exceeded |
| `500` | Server error |
