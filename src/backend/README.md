# We Whacked Backend

FastAPI-based backend service for the We Whacked application.

## Setup

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy the environment file:
```bash
cp .env.example .env
```

### Running the Server

Start the development server:
```bash
python -m backend.main
```

Or using uvicorn directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── main.py              # Main application entry point
├── config.py            # Configuration settings
├── routes/
│   ├── __init__.py
│   ├── health.py        # Health check endpoints
│   └── api.py           # Main API endpoints
├── requirements.txt     # Python dependencies
└── .env.example         # Example environment variables
```

## Available Endpoints

- `GET /` - Welcome message
- `GET /health/` - Health check
- `GET /api/` - API information
- `POST /api/echo` - Echo endpoint

## Development

The backend uses:
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
