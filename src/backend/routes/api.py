"""Main API endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Message(BaseModel):
    """Message response model."""
    message: str


@router.get("/", response_model=Message)
async def get_api_info():
    """Get API information."""
    return Message(message="We Whacked API v0.1.0")


@router.post("/echo", response_model=Message)
async def echo(message: Message):
    """Echo back a message."""
    return message
