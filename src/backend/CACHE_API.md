# Cache API Documentation

## Overview

The Cache API provides a unified interface for accessing all cached data from the We Whacked application. This allows any current or future app to access shared data through simple API endpoints.

## Endpoints

### 1. Get Complete Cache Database
**Endpoint:** `GET /cache/database`

Returns the entire cache database with all data from all modules.

**Response:**
```json
{
  "timestamp": "2025-11-22T15:30:00",
  "caches": {
    "restrooms": {
      "data": [...],
      "timestamp": "2025-11-22T15:25:00"
    }
  },
  "summary": {
    "restrooms": {
      "key": "restrooms",
      "timestamp": "2025-11-22T15:25:00",
      "data_count": 8,
      "cache_age_seconds": 300.5
    }
  }
}
```

### 2. Get Specific Cache Data
**Endpoint:** `GET /cache/database/{cache_key}`

Retrieves data for a specific cache key.

**Parameters:**
- `cache_key` (string, path): The key of the cache to retrieve

**Example:**
```
GET /cache/database/restrooms
```

**Response:**
```json
{
  "data": [...],
  "timestamp": "2025-11-22T15:25:00"
}
```

### 3. Get Cache Summary
**Endpoint:** `GET /cache/summary`

Get metadata about all cached data without the actual data.

**Response:**
```json
{
  "timestamp": "2025-11-22T15:30:00",
  "total_caches": 1,
  "caches": {
    "restrooms": {
      "key": "restrooms",
      "timestamp": "2025-11-22T15:25:00",
      "data_count": 8,
      "cache_age_seconds": 300.5
    }
  }
}
```

### 4. Register New Cache (Dynamic)
**Endpoint:** `POST /cache/register/{cache_key}`

Register a new cache dynamically for future apps.

**Parameters:**
- `cache_key` (string, path): Unique identifier for the cache

**Request Body:**
```json
{
  "data": [...],
  "timestamp": "2025-11-22T15:25:00"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Cache 'events' registered successfully",
  "cache_key": "events"
}
```

## Available Caches

### Restrooms Cache
- **Key:** `restrooms`
- **TTL:** 1 hour
- **Data:** Boston public restrooms locations with coordinates, hours, and neighborhood
- **Endpoint:** `/cache/database/restrooms` or `/restrooms/`

## Example Usage

### Get all restrooms from cache
```bash
curl http://localhost:8000/cache/database/restrooms
```

### Get entire database for all apps
```bash
curl http://localhost:8000/cache/database
```

### Monitor cache health
```bash
curl http://localhost:8000/cache/summary
```

### Register a new app's cache
```bash
curl -X POST http://localhost:8000/cache/register/events \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "timestamp": "2025-11-22T15:25:00"
  }'
```

## For Future Apps

To register your app's cache:

1. Import and use `register_cache()`:
```python
from backend.routes.cache import register_cache

# After fetching/preparing your data
cache_data = {
    "data": your_data_list,
    "timestamp": datetime.now()
}
register_cache("my_feature_name", cache_data)
```

2. Your data is now accessible via:
   - `GET /cache/database` - included in full dump
   - `GET /cache/database/my_feature_name` - specific access
   - `GET /cache/summary` - metadata only

## Cache Behavior

- **Shared Registry:** All module caches are stored in a global registry
- **No TTL Enforcement:** Each module manages its own TTL (e.g., restrooms has 1 hour)
- **Real-time Access:** Cache data is returned as-is; modules update when needed
- **Extensible:** New caches can be added dynamically without code changes

## Response Codes

- `200` - Success
- `404` - Cache key not found
- `500` - Server error
