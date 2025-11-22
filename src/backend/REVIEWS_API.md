# Review API Documentation

## Overview

The Review API provides a complete system for managing location-based reviews. Users can submit reviews for specific map coordinates, and the system stores all data in pandas DataFrames for efficient querying and analysis.

## Architecture

- **Storage:** Pandas DataFrames persisted as Parquet files
- **Database:** Two tables - `reviews` and `locations`
- **Data Directory:** `src/backend/data/`
  - `reviews.parquet` - All review records
  - `locations.parquet` - Location metadata and aggregates

## Data Models

### Review
```json
{
  "review_id": "uuid",
  "location_id": "string",
  "latitude": 42.3554,
  "longitude": -71.0606,
  "title": "Great place",
  "content": "Very clean and accessible",
  "rating": 5,
  "author": "John Doe",
  "tags": ["clean", "accessible"],
  "created_at": "2025-11-22T15:30:00",
  "updated_at": "2025-11-22T15:30:00"
}
```

### Location
```json
{
  "location_id": "downtown-restroom-1",
  "latitude": 42.3554,
  "longitude": -71.0606,
  "review_count": 3,
  "average_rating": 4.5,
  "created_at": "2025-11-22T15:00:00"
}
```

## Endpoints

### 1. Create Review
**Endpoint:** `POST /reviews/reviews`

Submit a new review for a location.

**Request Body:**
```json
{
  "location_id": "downtown-restroom-1",
  "latitude": 42.3554,
  "longitude": -71.0606,
  "title": "Great facilities",
  "content": "Very clean and well-maintained restroom",
  "rating": 5,
  "author": "John Doe",
  "tags": ["clean", "accessible", "fast"]
}
```

**Response:** Created review with ID and timestamps
```json
{
  "review_id": "550e8400-e29b-41d4-a716-446655440000",
  "location_id": "downtown-restroom-1",
  "latitude": 42.3554,
  "longitude": -71.0606,
  "title": "Great facilities",
  "content": "Very clean and well-maintained restroom",
  "rating": 5,
  "author": "John Doe",
  "tags": ["clean", "accessible", "fast"],
  "created_at": "2025-11-22T15:30:00",
  "updated_at": "2025-11-22T15:30:00"
}
```

### 2. Get All Reviews
**Endpoint:** `GET /reviews/reviews`

Retrieve all reviews in the database.

**Response:**
```json
{
  "total": 42,
  "reviews": [
    {
      "review_id": "...",
      "location_id": "...",
      ...
    }
  ]
}
```

### 3. Get Reviews by Location
**Endpoint:** `GET /reviews/reviews/location/{location_id}`

Get all reviews for a specific location.

**Parameters:**
- `location_id` (path): Location identifier

**Example:**
```
GET /reviews/reviews/location/downtown-restroom-1
```

**Response:**
```json
{
  "total": 5,
  "reviews": [...]
}
```

### 4. Get Specific Review
**Endpoint:** `GET /reviews/reviews/id/{review_id}`

Retrieve a single review by ID.

**Parameters:**
- `review_id` (path): Review identifier (UUID)

### 5. Delete Review
**Endpoint:** `DELETE /reviews/reviews/{review_id}`

Remove a review from the database.

**Response:**
```json
{
  "status": "success",
  "message": "Review deleted",
  "review_id": "..."
}
```

### 6. Get All Locations
**Endpoint:** `GET /reviews/locations`

Get all locations that have reviews.

**Response:**
```json
{
  "total": 10,
  "locations": [
    {
      "location_id": "downtown-restroom-1",
      "latitude": 42.3554,
      "longitude": -71.0606,
      "review_count": 5,
      "average_rating": 4.5,
      "created_at": "2025-11-22T15:00:00"
    }
  ]
}
```

### 7. Get Nearby Locations
**Endpoint:** `GET /reviews/locations/nearby?latitude=X&longitude=Y&radius_miles=5`

Find locations with reviews within a search radius.

**Parameters:**
- `latitude` (float, query): Center latitude
- `longitude` (float, query): Center longitude
- `radius_miles` (float, query, default: 5.0): Search radius

**Example:**
```
GET /reviews/locations/nearby?latitude=42.3554&longitude=-71.0606&radius_miles=2
```

### 8. Get Location with Reviews
**Endpoint:** `GET /reviews/locations/{location_id}`

Get a location and all its reviews combined.

**Parameters:**
- `location_id` (path): Location identifier

**Response:**
```json
{
  "location_id": "downtown-restroom-1",
  "latitude": 42.3554,
  "longitude": -71.0606,
  "review_count": 5,
  "average_rating": 4.5,
  "reviews": [...]
}
```

### 9. Get Review Statistics
**Endpoint:** `GET /reviews/stats`

Get aggregate statistics about reviews and locations.

**Response:**
```json
{
  "total_reviews": 42,
  "total_locations": 8,
  "average_rating": 4.3,
  "top_reviewed_locations": [
    {
      "location_id": "downtown-restroom-1",
      "review_count": 12,
      "average_rating": 4.7
    }
  ]
}
```

### 10. Export Reviews as CSV
**Endpoint:** `GET /reviews/export/reviews`

Download all reviews as a CSV file.

**Response:** CSV file download

## Usage Examples

### Submit a review from a map
```bash
curl -X POST http://localhost:8000/reviews/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": "downtown-restroom-1",
    "latitude": 42.3554,
    "longitude": -71.0606,
    "title": "Clean and accessible",
    "content": "Great restroom facility",
    "rating": 5,
    "author": "Jane Smith",
    "tags": ["clean", "accessible"]
  }'
```

### Get all reviews for a location
```bash
curl http://localhost:8000/reviews/reviews/location/downtown-restroom-1
```

### Find nearby locations with reviews
```bash
curl "http://localhost:8000/reviews/locations/nearby?latitude=42.3554&longitude=-71.0606&radius_miles=2"
```

### View location with all reviews
```bash
curl http://localhost:8000/reviews/locations/downtown-restroom-1
```

### Get statistics
```bash
curl http://localhost:8000/reviews/stats
```

## Map Integration Flow

1. **User selects location on map** (frontend)
2. **Frontend extracts coordinates** (latitude, longitude)
3. **POST /reviews/reviews** with location details and review
4. **Review saved** to reviews DataFrame
5. **Location created/updated** in locations DataFrame with aggregates
6. **User can query** nearby locations or specific reviews

## Frontend Integration

### Typical review submission from map:
```javascript
async function submitReview(mapCoordinates, reviewData) {
  const payload = {
    location_id: `location-${Date.now()}`,
    latitude: mapCoordinates.lat,
    longitude: mapCoordinates.lng,
    title: reviewData.title,
    content: reviewData.content,
    rating: reviewData.rating,
    author: reviewData.author,
    tags: reviewData.tags
  };
  
  const response = await fetch('/reviews/reviews', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  return response.json();
}
```

### Display nearby reviews on map:
```javascript
async function getLocationReviews(lat, lng, radius) {
  const response = await fetch(
    `/reviews/locations/nearby?latitude=${lat}&longitude=${lng}&radius_miles=${radius}`
  );
  return response.json();
}
```

## Data Persistence

- **Format:** Apache Parquet (efficient columnar format)
- **Location:** `src/backend/data/`
- **Auto-initialization:** DataFrames created on first request if missing
- **Atomic operations:** All DataFrame operations are atomic to prevent corruption

## Performance Characteristics

- **Read:** O(n) - Full scan of DataFrame
- **Write:** O(n) - Append and recalculate aggregates
- **Search:** O(n) - Filter by location_id
- **Nearby:** O(n) - Filter by distance calculation

For large datasets (>10k reviews), consider migrating to a proper database (PostgreSQL, MongoDB).
