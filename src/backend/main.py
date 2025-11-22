"""Main entry point for the FastAPI backend service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes import health, api, restrooms, cache, reviews

# Create FastAPI app
app = FastAPI(
    title="We Whacked API",
    description="Backend API for We Whacked",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(api.router, prefix="/api", tags=["api"])
app.include_router(restrooms.router, prefix="/restrooms", tags=["restrooms"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(cache.router, prefix="/cache", tags=["cache"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint returning API information."""
    return JSONResponse({
        "message": "Welcome to We Whacked API",
        "version": "0.1.0",
        "docs": "/docs"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
