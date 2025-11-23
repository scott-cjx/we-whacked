"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Check if the API is running."""
    return HealthResponse(status="healthy")
