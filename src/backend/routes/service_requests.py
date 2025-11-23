"""Service request management endpoints using pandas DataFrames."""

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from pathlib import Path

router = APIRouter()
from backend.routes import reviews as reviews_module

# Data directory for storing DataFrames
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

SERVICE_REQUESTS_DB_PATH = DATA_DIR / "service_requests.parquet"


class ServiceRequestCreate(BaseModel):
    """Model for creating a service request."""
    request_type: str  # "ramp", "parking", "signage", "restroom", "other"
    location_id: Optional[str] = None
    latitude: float
    longitude: float
    address: str
    description: str
    priority: str = "medium"  # "low", "medium", "high"
    requester_name: str
    requester_email: Optional[str] = None


class ServiceRequest(ServiceRequestCreate):
    """Service request model with metadata."""
    request_id: str
    status: str  # "pending", "in-progress", "completed", "rejected"
    created_at: datetime
    updated_at: datetime


class ServiceRequestResponse(BaseModel):
    """Response model for service requests."""
    total: int
    requests: List[ServiceRequest]


class ServiceRequestUpdate(BaseModel):
    """Model for updating service request status."""
    status: str
    notes: Optional[str] = None


def _initialize_dataframe():
    """Initialize service requests DataFrame if it doesn't exist."""
    if not SERVICE_REQUESTS_DB_PATH.exists():
        df = pd.DataFrame(columns=[
            'request_id', 'request_type', 'location_id', 'latitude', 'longitude',
            'address', 'description', 'priority', 'status',
            'requester_name', 'requester_email',
            'created_at', 'updated_at'
        ])
        df.to_parquet(SERVICE_REQUESTS_DB_PATH)


def _load_df() -> pd.DataFrame:
    """Load service requests DataFrame."""
    _initialize_dataframe()
    return pd.read_parquet(SERVICE_REQUESTS_DB_PATH)


def _save_df(df: pd.DataFrame):
    """Save service requests DataFrame."""
    df.to_parquet(SERVICE_REQUESTS_DB_PATH)


def _generate_id() -> str:
    """Generate a unique ID."""
    import uuid
    return str(uuid.uuid4())


@router.post("/", response_model=ServiceRequest)
async def create_service_request(request: ServiceRequestCreate):
    """Create a new service request.
    
    Args:
        request: Service request data
    
    Returns:
        Created service request with metadata
    """
    try:
        df = _load_df()
        now = datetime.now()
        request_id = _generate_id()
        
        # Validate request type
        valid_types = ["ramp", "parking", "signage", "restroom", "other"]
        if request.request_type.lower() not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request_type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Validate priority
        valid_priorities = ["low", "medium", "high"]
        if request.priority.lower() not in valid_priorities:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
            )
        
        # Create request record
        request_data = {
            'request_id': request_id,
            'request_type': request.request_type.lower(),
            'location_id': request.location_id,
            'latitude': request.latitude,
            'longitude': request.longitude,
            'address': request.address,
            'description': request.description,
            'priority': request.priority.lower(),
            'status': 'pending',
            'requester_name': request.requester_name,
            'requester_email': request.requester_email,
            'created_at': now,
            'updated_at': now
        }
        
        # Add to DataFrame
        df = pd.concat([df, pd.DataFrame([request_data])], ignore_index=True)
        _save_df(df)
        
        return ServiceRequest(**request_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=ServiceRequestResponse)
async def get_all_service_requests(
    status: Optional[str] = None,
    request_type: Optional[str] = None,
    priority: Optional[str] = None
):
    """Get all service requests with optional filters.
    
    Args:
        status: Filter by status (pending, in-progress, completed, rejected)
        request_type: Filter by request type
        priority: Filter by priority (low, medium, high)
    
    Returns:
        Service requests matching filters
    """
    try:
        df = _load_df()
        
        # Apply filters
        if status:
            df = df[df['status'] == status.lower()]
        if request_type:
            df = df[df['request_type'] == request_type.lower()]
        if priority:
            df = df[df['priority'] == priority.lower()]
        
        if df.empty:
            return ServiceRequestResponse(total=0, requests=[])
        
        requests = []
        for _, row in df.iterrows():
            req = ServiceRequest(
                request_id=row['request_id'],
                request_type=row['request_type'],
                location_id=row['location_id'] if pd.notna(row['location_id']) else None,
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                address=row['address'],
                description=row['description'],
                priority=row['priority'],
                status=row['status'],
                requester_name=row['requester_name'],
                requester_email=row['requester_email'] if pd.notna(row['requester_email']) else None,
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            requests.append(req)
        
        return ServiceRequestResponse(total=len(requests), requests=requests)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{request_id}", response_model=ServiceRequest)
async def get_service_request(request_id: str):
    """Get a specific service request by ID.
    
    Args:
        request_id: The request ID
    
    Returns:
        The service request
    """
    try:
        df = _load_df()
        request_row = df[df['request_id'] == request_id]
        
        if request_row.empty:
            raise HTTPException(status_code=404, detail=f"Service request '{request_id}' not found")
        
        row = request_row.iloc[0]
        return ServiceRequest(
            request_id=row['request_id'],
            request_type=row['request_type'],
            location_id=row['location_id'] if pd.notna(row['location_id']) else None,
            latitude=float(row['latitude']),
            longitude=float(row['longitude']),
            address=row['address'],
            description=row['description'],
            priority=row['priority'],
            status=row['status'],
            requester_name=row['requester_name'],
            requester_email=row['requester_email'] if pd.notna(row['requester_email']) else None,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/{request_id}/status")
async def update_service_request_status(request_id: str, update: ServiceRequestUpdate):
    """Update the status of a service request.
    
    Args:
        request_id: The request ID
        update: Status update data
    
    Returns:
        Updated service request
    """
    try:
        df = _load_df()
        
        if request_id not in df['request_id'].values:
            raise HTTPException(status_code=404, detail=f"Service request '{request_id}' not found")
        
        # Validate status
        valid_statuses = ["pending", "in-progress", "completed", "rejected"]
        if update.status.lower() not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Update status
        idx = df[df['request_id'] == request_id].index[0]
        df.at[idx, 'status'] = update.status.lower()
        df.at[idx, 'updated_at'] = datetime.now()
        
        _save_df(df)
        
        row = df.iloc[idx]
        return ServiceRequest(
            request_id=row['request_id'],
            request_type=row['request_type'],
            location_id=row['location_id'] if pd.notna(row['location_id']) else None,
            latitude=float(row['latitude']),
            longitude=float(row['longitude']),
            address=row['address'],
            description=row['description'],
            priority=row['priority'],
            status=row['status'],
            requester_name=row['requester_name'],
            requester_email=row['requester_email'] if pd.notna(row['requester_email']) else None,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{request_id}")
async def delete_service_request(request_id: str):
    """Delete a service request by ID.
    
    Args:
        request_id: The request to delete
    
    Returns:
        Confirmation message
    """
    try:
        df = _load_df()
        
        if request_id not in df['request_id'].values:
            raise HTTPException(status_code=404, detail=f"Service request '{request_id}' not found")
        
        df = df[df['request_id'] != request_id]
        _save_df(df)
        
        return {
            "status": "success",
            "message": f"Service request '{request_id}' deleted",
            "request_id": request_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/stats/summary")
async def get_stats():
    """Get statistics about service requests.
    
    Returns:
        Service request statistics
    """
    try:
        df = _load_df()
        
        if df.empty:
            return {
                "total": 0,
                "by_status": {},
                "by_type": {},
                "by_priority": {}
            }
        
        return {
            "total": len(df),
            "by_status": df['status'].value_counts().to_dict(),
            "by_type": df['request_type'].value_counts().to_dict(),
            "by_priority": df['priority'].value_counts().to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/db/all")
async def get_all_db_contents():
    """Return all stored data (service requests, reviews, locations) as JSON.

    This is an administrative/debug endpoint that dumps the content of the
    parquet-backed DataFrames. Datetime fields are ISO-encoded for JSON.
    """
    try:
        # Load dataframes
        sr_df = _load_df()
        reviews_df = reviews_module._load_reviews_df()
        locations_df = reviews_module._load_locations_df()

        def row_to_dict(row, datetime_fields=None):
            d = {}
            for k, v in row.items():
                if datetime_fields and k in datetime_fields:
                    try:
                        d[k] = v.isoformat() if v is not None and hasattr(v, 'isoformat') else None
                    except Exception:
                        d[k] = str(v)
                else:
                    # Convert numpy types to native Python types
                    try:
                        if pd.isna(v):
                            d[k] = None
                        else:
                            d[k] = v.item() if hasattr(v, 'item') else v
                    except Exception:
                        d[k] = v
            return d

        service_requests = []
        sr_dt_fields = ['created_at', 'updated_at']
        for _, row in sr_df.iterrows():
            service_requests.append(row_to_dict(row, datetime_fields=sr_dt_fields))

        reviews = []
        rev_dt_fields = ['created_at', 'updated_at']
        for _, row in reviews_df.iterrows():
            reviews.append(row_to_dict(row, datetime_fields=rev_dt_fields))

        locations = []
        loc_dt_fields = ['created_at', 'updated_at']
        for _, row in locations_df.iterrows():
            locations.append(row_to_dict(row, datetime_fields=loc_dt_fields))

        return {
            'service_requests': service_requests,
            'reviews': reviews,
            'locations': locations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")