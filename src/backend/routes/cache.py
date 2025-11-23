"""Cache management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter()


class CacheInfo(BaseModel):
    """Cache metadata."""
    key: str
    timestamp: Optional[datetime] = None
    data_count: int
    cache_age_seconds: Optional[float] = None


class CacheDatabaseResponse(BaseModel):
    """Response model for full cache database."""
    timestamp: datetime
    caches: Dict[str, Any]
    summary: Dict[str, CacheInfo]


# Global cache registry - all cache data from all modules
_cache_registry: Dict[str, Dict[str, Any]] = {}


def register_cache(key: str, cache_dict: Dict[str, Any]) -> None:
    """Register a cache from any module.
    
    Args:
        key: Unique cache key (e.g., 'restrooms', 'events', 'services')
        cache_dict: The cache dictionary to register
    """
    _cache_registry[key] = cache_dict


def get_all_caches() -> Dict[str, Dict[str, Any]]:
    """Get all registered caches.
    
    Returns:
        Dictionary of all registered caches
    """
    return _cache_registry.copy()


def get_cache_summary() -> Dict[str, CacheInfo]:
    """Get summary information for all caches.
    
    Returns:
        Summary info for each registered cache
    """
    summary = {}
    for key, cache in _cache_registry.items():
        data = cache.get("data")
        timestamp = cache.get("timestamp")
        
        data_count = 0
        if isinstance(data, list):
            data_count = len(data)
        elif isinstance(data, dict):
            data_count = len(data)
        
        cache_age = None
        if timestamp:
            from datetime import datetime
            cache_age = (datetime.now() - timestamp).total_seconds()
        
        summary[key] = CacheInfo(
            key=key,
            timestamp=timestamp,
            data_count=data_count,
            cache_age_seconds=cache_age
        )
    
    return summary


@router.get("/database", response_model=CacheDatabaseResponse)
async def get_cache_database():
    """Get the entire cache database for all apps.
    
    This endpoint returns all cached data from all modules,
    allowing any current or future app to access shared data.
    
    Returns:
        Complete cache database with metadata
    """
    try:
        caches = get_all_caches()
        summary = get_cache_summary()
        
        return CacheDatabaseResponse(
            timestamp=datetime.now(),
            caches=caches,
            summary=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/database/{cache_key}")
async def get_cache_by_key(cache_key: str):
    """Get specific cache data by key.
    
    Args:
        cache_key: The cache key to retrieve
    
    Returns:
        The cache data for the specified key
    """
    try:
        caches = get_all_caches()
        
        if cache_key not in caches:
            raise HTTPException(
                status_code=404,
                detail=f"Cache '{cache_key}' not found. Available caches: {list(caches.keys())}"
            )
        
        return caches[cache_key]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/summary")
async def get_cache_summary_endpoint():
    """Get summary of all cached data.
    
    Returns:
        Summary information for each cache
    """
    try:
        summary = get_cache_summary()
        return {
            "timestamp": datetime.now(),
            "total_caches": len(summary),
            "caches": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/register/{cache_key}")
async def register_cache_endpoint(cache_key: str, cache_data: Dict[str, Any]):
    """Register a new cache dynamically.
    
    Args:
        cache_key: Unique key for the cache
        cache_data: The cache dictionary to register
    
    Returns:
        Confirmation message
    """
    try:
        register_cache(cache_key, cache_data)
        return {
            "status": "success",
            "message": f"Cache '{cache_key}' registered successfully",
            "cache_key": cache_key
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
