"""Review management endpoints using pandas DataFrames."""

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

router = APIRouter()

# Data directory for storing DataFrames
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

REVIEWS_DB_PATH = DATA_DIR / "reviews.parquet"
LOCATIONS_DB_PATH = DATA_DIR / "locations.parquet"


class ReviewCreate(BaseModel):
    """Model for creating a review."""
    location_id: str
    latitude: float
    longitude: float
    title: str
    content: str
    rating: int  # 1-5 stars
    author: str
    tags: Optional[List[str]] = None


class Review(ReviewCreate):
    """Review model with metadata."""
    review_id: str
    created_at: datetime
    updated_at: datetime


class ReviewResponse(BaseModel):
    """Response model for reviews."""
    total: int
    reviews: List[Review]


class LocationReview(BaseModel):
    """Location with its reviews."""
    location_id: str
    latitude: float
    longitude: float
    review_count: int
    average_rating: Optional[float]
    reviews: List[Review]


class Location(BaseModel):
    """Location model."""
    location_id: str
    latitude: float
    longitude: float
    created_at: datetime
    review_count: int
    average_rating: Optional[float]


class LocationsResponse(BaseModel):
    """Response model for locations."""
    total: int
    locations: List[Location]


def _initialize_dataframes():
    """Initialize DataFrames if they don't exist."""
    if not REVIEWS_DB_PATH.exists():
        reviews_df = pd.DataFrame(columns=[
            'review_id', 'location_id', 'latitude', 'longitude', 
            'title', 'content', 'rating', 'author', 'tags',
            'created_at', 'updated_at'
        ])
        reviews_df.to_parquet(REVIEWS_DB_PATH)
    
    if not LOCATIONS_DB_PATH.exists():
        locations_df = pd.DataFrame(columns=[
            'location_id', 'latitude', 'longitude', 
            'created_at', 'review_count', 'average_rating'
        ])
        locations_df.to_parquet(LOCATIONS_DB_PATH)


def _load_reviews_df() -> pd.DataFrame:
    """Load reviews DataFrame."""
    _initialize_dataframes()
    return pd.read_parquet(REVIEWS_DB_PATH)


def _load_locations_df() -> pd.DataFrame:
    """Load locations DataFrame."""
    _initialize_dataframes()
    return pd.read_parquet(LOCATIONS_DB_PATH)


def _save_reviews_df(df: pd.DataFrame):
    """Save reviews DataFrame."""
    df.to_parquet(REVIEWS_DB_PATH)


def _save_locations_df(df: pd.DataFrame):
    """Save locations DataFrame."""
    df.to_parquet(LOCATIONS_DB_PATH)


def _generate_id() -> str:
    """Generate a unique ID."""
    import uuid
    return str(uuid.uuid4())


@router.post("/reviews", response_model=Review)
async def create_review(review: ReviewCreate):
    """Create a new review for a location.
    
    Args:
        review: Review data
    
    Returns:
        Created review with metadata
    """
    try:
        reviews_df = _load_reviews_df()
        locations_df = _load_locations_df()
        
        now = datetime.now()
        review_id = _generate_id()
        
        # Create review record
        review_data = {
            'review_id': review_id,
            'location_id': review.location_id,
            'latitude': review.latitude,
            'longitude': review.longitude,
            'title': review.title,
            'content': review.content,
            'rating': review.rating,
            'author': review.author,
            'tags': review.tags or [],
            'created_at': now,
            'updated_at': now
        }
        
        # Add review to DataFrame
        reviews_df = pd.concat([reviews_df, pd.DataFrame([review_data])], ignore_index=True)
        _save_reviews_df(reviews_df)
        
        # Update or create location
        location_mask = locations_df['location_id'] == review.location_id
        if location_mask.any():
            # Update existing location
            idx = locations_df[location_mask].index[0]
            review_count = len(reviews_df[reviews_df['location_id'] == review.location_id])
            avg_rating = reviews_df[reviews_df['location_id'] == review.location_id]['rating'].mean()
            
            locations_df.at[idx, 'review_count'] = review_count
            locations_df.at[idx, 'average_rating'] = float(avg_rating)
            locations_df.at[idx, 'updated_at'] = now
        else:
            # Create new location
            location_data = {
                'location_id': review.location_id,
                'latitude': review.latitude,
                'longitude': review.longitude,
                'created_at': now,
                'updated_at': now,
                'review_count': 1,
                'average_rating': float(review.rating)
            }
            locations_df = pd.concat([locations_df, pd.DataFrame([location_data])], ignore_index=True)
        
        _save_locations_df(locations_df)
        
        return Review(**review_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/reviews", response_model=ReviewResponse)
async def get_all_reviews():
    """Get all reviews from the database.
    
    Returns:
        All reviews with metadata
    """
    try:
        reviews_df = _load_reviews_df()
        
        if reviews_df.empty:
            return ReviewResponse(total=0, reviews=[])
        
        reviews = []
        for _, row in reviews_df.iterrows():
            review = Review(
                review_id=row['review_id'],
                location_id=row['location_id'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                title=row['title'],
                content=row['content'],
                rating=int(row['rating']),
                author=row['author'],
                tags=row['tags'] if isinstance(row['tags'], list) else [],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            reviews.append(review)
        
        return ReviewResponse(total=len(reviews), reviews=reviews)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/reviews/location/{location_id}", response_model=ReviewResponse)
async def get_reviews_by_location(location_id: str):
    """Get all reviews for a specific location.
    
    Args:
        location_id: The location ID
    
    Returns:
        Reviews for that location
    """
    try:
        reviews_df = _load_reviews_df()
        location_reviews = reviews_df[reviews_df['location_id'] == location_id]
        
        if location_reviews.empty:
            return ReviewResponse(total=0, reviews=[])
        
        reviews = []
        for _, row in location_reviews.iterrows():
            review = Review(
                review_id=row['review_id'],
                location_id=row['location_id'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                title=row['title'],
                content=row['content'],
                rating=int(row['rating']),
                author=row['author'],
                tags=row['tags'] if isinstance(row['tags'], list) else [],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            reviews.append(review)
        
        return ReviewResponse(total=len(reviews), reviews=reviews)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/reviews/id/{review_id}", response_model=Review)
async def get_review_by_id(review_id: str):
    """Get a specific review by ID.
    
    Args:
        review_id: The review ID
    
    Returns:
        The review
    """
    try:
        reviews_df = _load_reviews_df()
        review_row = reviews_df[reviews_df['review_id'] == review_id]
        
        if review_row.empty:
            raise HTTPException(status_code=404, detail=f"Review '{review_id}' not found")
        
        row = review_row.iloc[0]
        return Review(
            review_id=row['review_id'],
            location_id=row['location_id'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            title=row['title'],
            content=row['content'],
            rating=int(row['rating']),
            author=row['author'],
            tags=row['tags'] if isinstance(row['tags'], list) else [],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/locations", response_model=LocationsResponse)
async def get_all_locations():
    """Get all locations with review metadata.
    
    Returns:
        All locations with review counts and average ratings
    """
    try:
        locations_df = _load_locations_df()
        
        if locations_df.empty:
            return LocationsResponse(total=0, locations=[])
        
        locations = []
        for _, row in locations_df.iterrows():
            location = Location(
                location_id=row['location_id'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                created_at=row['created_at'],
                review_count=int(row['review_count']),
                average_rating=float(row['average_rating']) if pd.notna(row['average_rating']) else None
            )
            locations.append(location)
        
        return LocationsResponse(total=len(locations), locations=locations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/locations/nearby", response_model=LocationsResponse)
async def get_nearby_locations(latitude: float, longitude: float, radius_miles: float = 5.0):
    """Get locations within a specified radius of coordinates.
    
    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius_miles: Search radius in miles (default: 5.0)
    
    Returns:
        Locations within the radius
    """
    try:
        from math import radians, cos, sin, asin, sqrt
        
        locations_df = _load_locations_df()
        
        if locations_df.empty:
            return LocationsResponse(total=0, locations=[])
        
        nearby = []
        for _, row in locations_df.iterrows():
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            
            # Haversine formula
            lon1, lat1, lon2, lat2 = map(radians, [longitude, latitude, lon, lat])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            miles = 3959 * c
            
            if miles <= radius_miles:
                location = Location(
                    location_id=row['location_id'],
                    latitude=lat,
                    longitude=lon,
                    created_at=row['created_at'],
                    review_count=int(row['review_count']),
                    average_rating=float(row['average_rating']) if pd.notna(row['average_rating']) else None
                )
                nearby.append(location)
        
        return LocationsResponse(total=len(nearby), locations=nearby)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/locations/{location_id}", response_model=LocationReview)
async def get_location_with_reviews(location_id: str):
    """Get a location with all its reviews.
    
    Args:
        location_id: The location ID
    
    Returns:
        Location with complete review list
    """
    try:
        locations_df = _load_locations_df()
        reviews_df = _load_reviews_df()
        
        location_row = locations_df[locations_df['location_id'] == location_id]
        if location_row.empty:
            raise HTTPException(status_code=404, detail=f"Location '{location_id}' not found")
        
        loc = location_row.iloc[0]
        location_reviews = reviews_df[reviews_df['location_id'] == location_id]
        
        reviews = []
        for _, row in location_reviews.iterrows():
            review = Review(
                review_id=row['review_id'],
                location_id=row['location_id'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                title=row['title'],
                content=row['content'],
                rating=int(row['rating']),
                author=row['author'],
                tags=row['tags'] if isinstance(row['tags'], list) else [],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            reviews.append(review)
        
        return LocationReview(
            location_id=loc['location_id'],
            latitude=float(loc['latitude']),
            longitude=float(loc['longitude']),
            review_count=int(loc['review_count']),
            average_rating=float(loc['average_rating']) if pd.notna(loc['average_rating']) else None,
            reviews=reviews
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/stats")
async def get_review_stats():
    """Get statistics about reviews and locations.
    
    Returns:
        Review and location statistics
    """
    try:
        reviews_df = _load_reviews_df()
        locations_df = _load_locations_df()
        
        total_reviews = len(reviews_df)
        total_locations = len(locations_df)
        
        avg_rating = None
        if not reviews_df.empty:
            avg_rating = float(reviews_df['rating'].mean())
        
        top_locations = []
        if not locations_df.empty:
            top_locs = locations_df.nlargest(5, 'review_count')
            for _, row in top_locs.iterrows():
                top_locations.append({
                    'location_id': row['location_id'],
                    'review_count': int(row['review_count']),
                    'average_rating': float(row['average_rating']) if pd.notna(row['average_rating']) else None
                })
        
        return {
            "total_reviews": total_reviews,
            "total_locations": total_locations,
            "average_rating": avg_rating,
            "top_reviewed_locations": top_locations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/reviews/{review_id}")
async def delete_review(review_id: str):
    """Delete a review by ID.
    
    Args:
        review_id: The review to delete
    
    Returns:
        Confirmation message
    """
    try:
        reviews_df = _load_reviews_df()
        locations_df = _load_locations_df()
        
        if review_id not in reviews_df['review_id'].values:
            raise HTTPException(status_code=404, detail=f"Review '{review_id}' not found")
        
        location_id = reviews_df[reviews_df['review_id'] == review_id]['location_id'].iloc[0]
        
        # Remove review
        reviews_df = reviews_df[reviews_df['review_id'] != review_id]
        _save_reviews_df(reviews_df)
        
        # Update location stats
        location_reviews = reviews_df[reviews_df['location_id'] == location_id]
        if location_reviews.empty:
            # Delete location if no reviews
            locations_df = locations_df[locations_df['location_id'] != location_id]
        else:
            # Update location stats
            idx = locations_df[locations_df['location_id'] == location_id].index[0]
            locations_df.at[idx, 'review_count'] = len(location_reviews)
            locations_df.at[idx, 'average_rating'] = float(location_reviews['rating'].mean())
        
        _save_locations_df(locations_df)
        
        return {
            "status": "success",
            "message": f"Review '{review_id}' deleted",
            "review_id": review_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/export/reviews")
async def export_reviews_csv():
    """Export all reviews as CSV.
    
    Returns:
        CSV export of reviews
    """
    try:
        import io
        from fastapi.responses import StreamingResponse
        
        reviews_df = _load_reviews_df()
        
        if reviews_df.empty:
            raise HTTPException(status_code=404, detail="No reviews found")
        
        output = io.StringIO()
        reviews_df.to_csv(output, index=False)
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=reviews.csv"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
