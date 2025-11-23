"""Chatbot endpoints using Google Gemini API with function calling."""

import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.config import settings
from backend.routes import reviews, service_requests

router = APIRouter()

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "model"
    content: str
    timestamp: Optional[datetime] = None
    function_call: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    function_called: Optional[Dict[str, Any]] = None
    conversation_history: List[ChatMessage]


# Define functions that the chatbot can call
def create_service_request_function(
    request_type: str,
    latitude: float,
    longitude: float,
    address: str,
    description: str,
    requester_name: str,
    priority: str = "medium",
    requester_email: str = None
) -> Dict[str, Any]:
    """Create a new accessibility service request.
    
    Args:
        request_type: Type of request (ramp, parking, signage, restroom, other)
        latitude: Location latitude
        longitude: Location longitude
        address: Street address
        description: Detailed description of the request
        requester_name: Name of person making request
        priority: Priority level (low, medium, high)
        requester_email: Email address (optional)
    
    Returns:
        Created service request
    """
    request_data = service_requests.ServiceRequestCreate(
        request_type=request_type,
        latitude=latitude,
        longitude=longitude,
        address=address,
        description=description,
        priority=priority,
        requester_name=requester_name,
        requester_email=requester_email
    )
    
    # Use the service requests module directly
    df = service_requests._load_df()
    now = datetime.now()
    request_id = service_requests._generate_id()
    
    request_dict = {
        'request_id': request_id,
        'request_type': request_type.lower(),
        'location_id': None,
        'latitude': latitude,
        'longitude': longitude,
        'address': address,
        'description': description,
        'priority': priority.lower(),
        'status': 'pending',
        'requester_name': requester_name,
        'requester_email': requester_email,
        'created_at': now,
        'updated_at': now
    }
    
    import pandas as pd
    df = pd.concat([df, pd.DataFrame([request_dict])], ignore_index=True)
    service_requests._save_df(df)
    
    return {
        "success": True,
        "request_id": request_id,
        "message": f"Service request created successfully with ID: {request_id}"
    }


def create_review_function(
    location_id: str,
    latitude: float,
    longitude: float,
    title: str,
    content: str,
    rating: int,
    author: str,
    tags: List[str] = None
) -> Dict[str, Any]:
    """Create an accessibility review for a location.
    
    Args:
        location_id: Unique identifier for the location
        latitude: Location latitude
        longitude: Location longitude
        title: Review title
        content: Review content/description
        rating: Rating from 1-5 stars
        author: Name of reviewer
        tags: Optional tags (e.g., ["wheelchair-accessible", "ramp"])
    
    Returns:
        Created review
    """
    review_data = reviews.ReviewCreate(
        location_id=location_id,
        latitude=latitude,
        longitude=longitude,
        title=title,
        content=content,
        rating=rating,
        author=author,
        tags=tags or []
    )
    
    # Use the reviews module directly
    import pandas as pd
    reviews_df = reviews._load_reviews_df()
    locations_df = reviews._load_locations_df()
    
    now = datetime.now()
    review_id = reviews._generate_id()
    
    review_dict = {
        'review_id': review_id,
        'location_id': location_id,
        'latitude': latitude,
        'longitude': longitude,
        'title': title,
        'content': content,
        'rating': rating,
        'author': author,
        'tags': tags or [],
        'created_at': now,
        'updated_at': now
    }
    
    reviews_df = pd.concat([reviews_df, pd.DataFrame([review_dict])], ignore_index=True)
    reviews._save_reviews_df(reviews_df)
    
    # Update location
    location_mask = locations_df['location_id'] == location_id
    if location_mask.any():
        idx = locations_df[location_mask].index[0]
        review_count = len(reviews_df[reviews_df['location_id'] == location_id])
        avg_rating = reviews_df[reviews_df['location_id'] == location_id]['rating'].mean()
        locations_df.at[idx, 'review_count'] = review_count
        locations_df.at[idx, 'average_rating'] = float(avg_rating)
    else:
        location_data = {
            'location_id': location_id,
            'latitude': latitude,
            'longitude': longitude,
            'created_at': now,
            'review_count': 1,
            'average_rating': float(rating)
        }
        locations_df = pd.concat([locations_df, pd.DataFrame([location_data])], ignore_index=True)
    
    reviews._save_locations_df(locations_df)
    
    return {
        "success": True,
        "review_id": review_id,
        "message": f"Review created successfully with ID: {review_id}"
    }


def search_locations_function(
    latitude: float = None,
    longitude: float = None,
    radius_miles: float = 5.0
) -> Dict[str, Any]:
    """Search for locations with reviews.
    
    Args:
        latitude: Search center latitude (optional)
        longitude: Search center longitude (optional)
        radius_miles: Search radius in miles (default: 5.0)
    
    Returns:
        List of locations with reviews
    """
    locations_df = reviews._load_locations_df()
    
    if locations_df.empty:
        return {"success": True, "locations": [], "count": 0}
    
    if latitude is not None and longitude is not None:
        from math import radians, cos, sin, asin, sqrt
        
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
                nearby.append({
                    "location_id": row['location_id'],
                    "latitude": lat,
                    "longitude": lon,
                    "review_count": int(row['review_count']),
                    "average_rating": float(row['average_rating']) if row['average_rating'] else None,
                    "distance_miles": round(miles, 2)
                })
        
        return {"success": True, "locations": nearby, "count": len(nearby)}
    else:
        # Return all locations
        all_locations = []
        for _, row in locations_df.iterrows():
            all_locations.append({
                "location_id": row['location_id'],
                "latitude": float(row['latitude']),
                "longitude": float(row['longitude']),
                "review_count": int(row['review_count']),
                "average_rating": float(row['average_rating']) if row['average_rating'] else None
            })
        
        return {"success": True, "locations": all_locations, "count": len(all_locations)}


def get_location_reviews_function(location_id: str) -> Dict[str, Any]:
    """Get all reviews for a specific location.
    
    Args:
        location_id: The location identifier
    
    Returns:
        Reviews for the location
    """
    reviews_df = reviews._load_reviews_df()
    location_reviews = reviews_df[reviews_df['location_id'] == location_id]
    
    if location_reviews.empty:
        return {"success": True, "reviews": [], "count": 0}
    
    review_list = []
    for _, row in location_reviews.iterrows():
        review_list.append({
            "review_id": row['review_id'],
            "title": row['title'],
            "content": row['content'],
            "rating": int(row['rating']),
            "author": row['author'],
            "tags": row['tags'] if isinstance(row['tags'], list) else [],
            "created_at": row['created_at'].isoformat()
        })
    
    return {"success": True, "reviews": review_list, "count": len(review_list)}


# System prompt for the chatbot
SYSTEM_INSTRUCTION = """You are MapAble Assistant, an AI helper for MapAble Boston - an accessibility-focused application that helps people find and rate accessible places in Boston.

Your capabilities:
1. Answer questions about accessibility in Boston and the MapAble app
2. Help users request accessibility improvements (ramps, parking, signage, restrooms, etc.)
3. Assist in submitting accessibility reviews for locations
4. Search and query existing location reviews and ratings

Guidelines:
- Be friendly, helpful, and empathetic
- Always ask for required information before creating service requests or reviews
- For service requests, you need: type, location (lat/lng), address, description, requester name
- For reviews, you need: location_id, location (lat/lng), title, content, rating (1-5), author name
- Provide helpful suggestions about accessibility in Boston
- Be concise but informative

When users want to create a service request or review, guide them through the process step by step."""


# Function declarations for Gemini
function_declarations = [
    {
        "name": "create_service_request",
        "description": "Create a new accessibility service request for improvements like ramps, parking, signage, or restrooms",
        "parameters": {
            "type": "object",
            "properties": {
                "request_type": {
                    "type": "string",
                    "description": "Type of request",
                    "enum": ["ramp", "parking", "signage", "restroom", "other"]
                },
                "latitude": {
                    "type": "number",
                    "description": "Location latitude"
                },
                "longitude": {
                    "type": "number",
                    "description": "Location longitude"
                },
                "address": {
                    "type": "string",
                    "description": "Street address of the location"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of the accessibility need"
                },
                "requester_name": {
                    "type": "string",
                    "description": "Name of the person making the request"
                },
                "priority": {
                    "type": "string",
                    "description": "Priority level (defaults to medium if not specified)",
                    "enum": ["low", "medium", "high"]
                },
                "requester_email": {
                    "type": "string",
                    "description": "Email address (optional)"
                }
            },
            "required": ["request_type", "latitude", "longitude", "address", "description", "requester_name"]
        }
    },
    {
        "name": "create_review",
        "description": "Create an accessibility review for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location_id": {
                    "type": "string",
                    "description": "Unique identifier for the location"
                },
                "latitude": {
                    "type": "number",
                    "description": "Location latitude"
                },
                "longitude": {
                    "type": "number",
                    "description": "Location longitude"
                },
                "title": {
                    "type": "string",
                    "description": "Review title"
                },
                "content": {
                    "type": "string",
                    "description": "Detailed review content"
                },
                "rating": {
                    "type": "integer",
                    "description": "Rating from 1-5 stars (must be between 1 and 5)"
                },
                "author": {
                    "type": "string",
                    "description": "Name of the reviewer"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags (e.g., wheelchair-accessible, ramp, elevator)"
                }
            },
            "required": ["location_id", "latitude", "longitude", "title", "content", "rating", "author"]
        }
    },
    {
        "name": "search_locations",
        "description": "Search for locations with accessibility reviews",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Search center latitude (optional)"
                },
                "longitude": {
                    "type": "number",
                    "description": "Search center longitude (optional)"
                },
                "radius_miles": {
                    "type": "number",
                    "description": "Search radius in miles (defaults to 5.0 if not specified)"
                }
            }
        }
    },
    {
        "name": "get_location_reviews",
        "description": "Get all accessibility reviews for a specific location",
        "parameters": {
            "type": "object",
            "properties": {
                "location_id": {
                    "type": "string",
                    "description": "The location identifier"
                }
            },
            "required": ["location_id"]
        }
    }
]


# Function mapping
FUNCTION_MAP = {
    "create_service_request": create_service_request_function,
    "create_review": create_review_function,
    "search_locations": search_locations_function,
    "get_location_reviews": get_location_reviews_function
}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages with Gemini AI.
    
    Args:
        request: Chat request with message and conversation history
    
    Returns:
        AI response with updated conversation history
    """
    try:
        if not settings.gemini_api_key:
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
            )
        
        # Initialize model with function calling (catch unsupported-model errors)
        try:
            model = genai.GenerativeModel(
                model_name=settings.gemini_model,
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[{"function_declarations": function_declarations}]
            )
        except Exception as e:
            # If model not found / unsupported for generateContent, try listing available models
            err_str = str(e)
            if "not found" in err_str.lower() or "404" in err_str or "models/" in err_str:
                try:
                    available = genai.list_models()
                    supported = [m.name for m in available if 'generateContent' in getattr(m, 'supported_generation_methods', [])]
                    suggestion = ', '.join(supported[:10]) if supported else 'No generateContent-capable models found.'
                except Exception:
                    suggestion = 'Could not fetch model list from API.'

                raise HTTPException(
                    status_code=500,
                    detail=(f"Requested model '{settings.gemini_model}' is not available or not supported for generation."
                            f" Error: {err_str}. Available generate-capable models: {suggestion}")
                )
            # Re-raise other exceptions
            raise
        
        # Build conversation history for Gemini (be defensive if None)
        history = []
        conv_hist = request.conversation_history or []
        for msg in conv_hist:
            # msg may be a dict coming from HTTP payload or a ChatMessage
            role = getattr(msg, 'role', None) or (msg.get('role') if isinstance(msg, dict) else None)
            content = getattr(msg, 'content', None) or (msg.get('content') if isinstance(msg, dict) else '')
            history.append({
                "role": role or "user",
                "parts": [content]
            })
        
        # Start chat with history
        chat_session = model.start_chat(history=history)
        
        # Send user message
        response = chat_session.send_message(request.message)
        
        # Check if function was called
        function_call_result = None
        response_text = ""

        # Prefer top-level `response.text` if present (handle str or list)
        if hasattr(response, 'text') and response.text:
            rt = response.text
            if isinstance(rt, (list, tuple)):
                response_text = ''.join(map(str, rt))
            else:
                response_text = str(rt)
        else:
            # Fall back to iterating content parts
            parts = getattr(response.candidates[0].content, 'parts', []) or []
            for part in parts:
                if hasattr(part, 'function_call'):
                    # Execute function; protect against conversion/parsing errors
                    try:
                        function_call = part.function_call
                        function_name = getattr(function_call, 'name', None)

                        # Safely extract function args; handle None, dict, iterable, or JSON string
                        raw_args = getattr(function_call, 'args', None)
                        function_args = {}
                        if raw_args is None:
                            function_args = {}
                        else:
                            try:
                                if isinstance(raw_args, dict):
                                    function_args = raw_args
                                else:
                                    # Try to coerce iterable of pairs to dict
                                    function_args = dict(raw_args)
                            except Exception:
                                # Try to parse JSON string
                                try:
                                    import json
                                    function_args = json.loads(raw_args)
                                except Exception:
                                    function_args = {}

                        if function_name in FUNCTION_MAP:
                            result = FUNCTION_MAP[function_name](**function_args)
                            function_call_result = {
                                "function_name": function_name,
                                "arguments": function_args,
                                "result": result
                            }

                            # Send function result back to model
                            function_response = chat_session.send_message({
                                "function_response": {
                                    "name": function_name,
                                    "response": result
                                }
                            })

                            # Get final text response safely
                            frt = getattr(function_response, 'text', None)
                            if frt:
                                if isinstance(frt, (list, tuple)):
                                    response_text += ''.join(map(str, frt))
                                else:
                                    response_text += str(frt)
                    except Exception as e:
                        # Don't raise 500; include a short diagnostic in the response and continue
                        try:
                            fn_name = function_call.name if 'function_call' in locals() and hasattr(function_call, 'name') else None
                            raw_args_preview = None
                            if 'raw_args' in locals():
                                try:
                                    raw_args_preview = str(raw_args)[:200]
                                except Exception:
                                    raw_args_preview = f"<unreprable {type(raw_args)}>"
                        except Exception:
                            fn_name = None
                            raw_args_preview = None

                        diag = (
                            f"\n[Debug] Could not process function_call '{fn_name}'; "
                            f"args_preview={raw_args_preview}; error={repr(e)}\n"
                        )
                        response_text += diag

                elif hasattr(part, 'text'):
                    pt = part.text
                    if isinstance(pt, (list, tuple)):
                        response_text += ''.join(map(str, pt))
                    else:
                        response_text += str(pt)
        
        # Build updated conversation history
        updated_history = (request.conversation_history or []).copy()
        updated_history.append(ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now()
        ))
        updated_history.append(ChatMessage(
            role="model",
            content=response_text,
            timestamp=datetime.now(),
            function_call=function_call_result
        ))
        
        return ChatResponse(
            message=response_text,
            function_called=function_call_result,
            conversation_history=updated_history
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if the chatbot service is healthy."""
    return {
        "status": "healthy",
        "gemini_configured": bool(settings.gemini_api_key),
        "model": settings.gemini_model
    }