"""Public restrooms endpoints."""

import aiohttp
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta

# Import cache management
from backend.routes.cache import register_cache

router = APIRouter()

# Boston public restrooms API endpoint
BOSTON_RESTROOMS_API = "https://data.boston.gov/api/3/action/datastore_search?resource_id=4f32efbe-e259-4755-8339-2027ee8d5ee5&limit=1000"

# Cache configuration
CACHE_TTL = timedelta(hours=1)
cache = {
    "data": None,
    "timestamp": None
}

# Mock data for fallback - Boston public restrooms
MOCK_RESTROOMS = [
    {
        "name": "Boston Public Library - Main Branch",
        "location": "700 Boylston Street",
        "address": "Boston, MA 02116",
        "hours": "Mon-Sat: 9AM-6PM, Sun: 1PM-5PM",
        "neighborhood": "Back Bay",
        "latitude": 42.3462,
        "longitude": -71.0726
    },
    {
        "name": "Downtown Boston Public Restroom",
        "location": "Downtown Crossing",
        "address": "Downtown, Boston, MA",
        "hours": "Daily: 7AM-10PM",
        "neighborhood": "Downtown",
        "latitude": 42.3554,
        "longitude": -71.0606
    },
    {
        "name": "Faneuil Hall Public Restroom",
        "location": "100 Hanover Street",
        "address": "Boston, MA 02109",
        "hours": "Daily: 10AM-9PM",
        "neighborhood": "Downtown",
        "latitude": 42.3631,
        "longitude": -71.0551
    },
    {
        "name": "Boston Common Public Restroom",
        "location": "Boston Common",
        "address": "Boston, MA 02108",
        "hours": "Daily: 8AM-6PM",
        "neighborhood": "Downtown",
        "latitude": 42.3565,
        "longitude": -71.0657
    },
    {
        "name": "Seaport District Public Restroom",
        "location": "Seaport Boulevard",
        "address": "Boston, MA 02210",
        "hours": "Daily: 9AM-9PM",
        "neighborhood": "Seaport",
        "latitude": 42.3618,
        "longitude": -71.0432
    },
    {
        "name": "Harvard Square Public Restroom",
        "location": "Harvard Square",
        "address": "Cambridge, MA 02138",
        "hours": "Daily: 7AM-11PM",
        "neighborhood": "Cambridge",
        "latitude": 42.3735,
        "longitude": -71.1194
    },
    {
        "name": "Back Bay Station Public Restroom",
        "location": "145 Dartmouth Street",
        "address": "Boston, MA 02116",
        "hours": "Daily: 6AM-10PM",
        "neighborhood": "Back Bay",
        "latitude": 42.3475,
        "longitude": -71.0751
    },
    {
        "name": "South Station Public Restroom",
        "location": "700 Atlantic Avenue",
        "address": "Boston, MA 02210",
        "hours": "Daily: 5AM-11PM",
        "neighborhood": "Downtown",
        "latitude": 42.3525,
        "longitude": -71.0552
    },
]


class Restroom(BaseModel):
    """Restroom location model."""
    name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    hours: Optional[str] = None
    neighborhood: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RestroomsResponse(BaseModel):
    """Response model for restrooms."""
    total: int
    restrooms: List[Restroom]


async def _get_cached_restrooms() -> List[dict]:
    """Fetch restrooms data with caching (1 hour TTL).
    
    Returns:
        List of restroom records from cache or API
    """
    now = datetime.now()
    
    # Check if cache is still valid
    if cache["data"] is not None and cache["timestamp"] is not None:
        age = now - cache["timestamp"]
        if age < CACHE_TTL:
            return cache["data"]
    
    # Cache is expired or empty - try to fetch from API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BOSTON_RESTROOMS_API, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    records = data.get("result", {}).get("records", [])
                    
                    # Update cache
                    cache["data"] = records
                    cache["timestamp"] = now
                    # Register in global cache registry
                    register_cache("restrooms", cache)
                    return records
    except (aiohttp.ClientError, asyncio.TimeoutError, Exception):
        # Fall back to mock data or existing cache
        pass
    
    # Use mock data as fallback
    cache["data"] = MOCK_RESTROOMS
    cache["timestamp"] = now
    # Register in global cache registry
    register_cache("restrooms", cache)
    return MOCK_RESTROOMS


@router.get("/", response_model=RestroomsResponse)
async def get_public_restrooms():
    """Get list of public restrooms in Boston."""
    try:
        records = await _get_cached_restrooms()
        
        restrooms: List[Restroom] = []
        for record in records:
            restroom = Restroom(
                name=record.get("name"),
                location=record.get("location"),
                address=record.get("address"),
                hours=record.get("hours"),
                neighborhood=record.get("neighborhood"),
                latitude=record.get("latitude"),
                longitude=record.get("longitude"),
            )
            restrooms.append(restroom)
        
        return RestroomsResponse(total=len(restrooms), restrooms=restrooms)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/nearby", response_model=RestroomsResponse)
async def get_nearby_restrooms(latitude: float, longitude: float, radius_miles: float = 1.0):
    """Get nearby restrooms based on coordinates.
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        radius_miles: Search radius in miles (default: 1.0)
    
    Returns:
        Filtered list of nearby restrooms
    """
    try:
        records = await _get_cached_restrooms()
        nearby: List[Restroom] = []
        
        for record in records:
            try:
                lat = float(record.get("latitude", 0))
                lon = float(record.get("longitude", 0))
                
                # Haversine formula for distance calculation
                lon1, lat1, lon2, lat2 = map(radians, [longitude, latitude, lon, lat])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                miles = 3959 * c  # Earth's radius in miles
                
                if miles <= radius_miles:
                    restroom = Restroom(
                        name=record.get("name"),
                        location=record.get("location"),
                        address=record.get("address"),
                        hours=record.get("hours"),
                        neighborhood=record.get("neighborhood"),
                        latitude=lat,
                        longitude=lon,
                    )
                    nearby.append(restroom)
            except (ValueError, TypeError):
                continue
        
        return RestroomsResponse(total=len(nearby), restrooms=nearby)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/neighborhood/{neighborhood}", response_model=RestroomsResponse)
async def get_restrooms_by_neighborhood(neighborhood: str):
    """Get public restrooms in a specific Boston neighborhood.
    
    Args:
        neighborhood: Neighborhood name (e.g., "Downtown", "Back Bay")
    
    Returns:
        Restrooms in the specified neighborhood
    """
    try:
        records = await _get_cached_restrooms()
        filtered: List[Restroom] = []
        
        for record in records:
            if record.get("neighborhood", "").lower() == neighborhood.lower():
                restroom = Restroom(
                    name=record.get("name"),
                    location=record.get("location"),
                    address=record.get("address"),
                    hours=record.get("hours"),
                    neighborhood=record.get("neighborhood"),
                    latitude=record.get("latitude"),
                    longitude=record.get("longitude"),
                )
                filtered.append(restroom)
        
        return RestroomsResponse(total=len(filtered), restrooms=filtered)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
