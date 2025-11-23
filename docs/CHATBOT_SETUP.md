# AI Chatbot Setup Guide

This guide will help you set up and use the AI-powered chatbot feature for MapAble Boston.

## Prerequisites

1. Python 3.11+
2. Google Gemini API Key (get one at https://makersuite.google.com/app/apikey)

## Installation

### 1. Install Dependencies

```bash
pip install -e .
```

This will install all required dependencies including:
- `google-generativeai` - For Gemini AI integration
- `fastapi` - Backend API framework
- `streamlit` - Frontend framework
- `pandas` & `pyarrow` - Data management

### 2. Configure Environment Variables

Create a `.env` file in the `src/backend/` directory:

```bash
cd src/backend
cp .env.example .env
```

Edit the `.env` file and add your Gemini API key:

```env
APP_NAME="We Whacked API"
APP_VERSION="0.1.0"
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Gemini AI Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Important:** Replace `your_actual_gemini_api_key_here` with your actual API key from Google AI Studio.

## Running the Application

### Option 1: Using the Run Script (Recommended)

```bash
./scripts/run_servers.sh
```

This will start both the backend and frontend servers.

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd src/backend
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd src/frontend
streamlit run main.py
```

## Using the Chatbot

### Accessing the Chatbot

1. Open your browser to the Streamlit URL (usually http://localhost:8501)
2. Click on "AI Assistant" from the home page or select it from the menu
3. Start chatting!

### What Can the Chatbot Do?

The AI Assistant can help you with:

#### 1. General Questions
Ask about accessibility in Boston, app features, or general information.

**Example prompts:**
- "What can this app do?"
- "Tell me about accessible places in Boston"
- "How do I find wheelchair-accessible restaurants?"

#### 2. Create Service Requests
Request accessibility improvements like ramps, parking, signage, etc.

**Example conversation:**
```
You: I need a wheelchair ramp installed at 123 Main St
Bot: I can help you create a service request. Could you provide:
     - The exact location (latitude/longitude)
     - Priority level (low/medium/high)
     - Your name
     - Detailed description of the need

You: The location is at coordinates 42.3601, -71.0589. This is a high priority 
     request. My name is John Doe. We need a ramp because the entrance has 3 steps
     with no alternative access.

Bot: [Creates service request and confirms]
```

#### 3. Submit Reviews
Share accessibility reviews for locations.

**Example conversation:**
```
You: I want to submit a review for the Boston Public Library
Bot: I can help you create a review. I'll need:
     - Location ID
     - Coordinates (latitude/longitude)
     - Review title
     - Detailed content
     - Rating (1-5 stars)
     - Your name

You: Location ID is "bpl_main", coordinates are 42.3493, -71.0776. 
     Title: "Excellent Accessibility". Content: "The library has 
     automatic doors, elevators, and wheelchair-accessible restrooms. 
     Staff is very helpful." Rating: 5 stars. Author: Jane Smith

Bot: [Creates review and confirms]
```

#### 4. Search Locations
Find and query existing location data.

**Example prompts:**
- "Show me accessible locations near downtown Boston"
- "What reviews are there for location ID 'boston_common'?"
- "Find accessible places within 2 miles of coordinates 42.36, -71.06"

## Testing the Features

### Test 1: General Question
```
Prompt: "What is MapAble Boston?"
Expected: Informative response about the app's purpose
```

### Test 2: Service Request
```
Prompt: "I need to request a wheelchair ramp at 100 Boylston St, Boston. 
        Coordinates: 42.3521, -71.0656. This is a medium priority. 
        My name is Test User. The entrance currently has stairs with no ramp."

Expected: 
- Bot asks for any missing information
- Creates service request when all info is provided
- Shows confirmation with request ID
```

### Test 3: Review Submission
```
Prompt: "Create a review for Faneuil Hall. Location ID: faneuil_hall, 
        coordinates: 42.3601, -71.0549. Title: 'Good accessibility', 
        Content: 'Ramps available, accessible restrooms, friendly staff', 
        Rating: 4, Author: Review Test"

Expected:
- Creates review successfully
- Shows confirmation with review ID
```

### Test 4: Location Search
```
Prompt: "Show me all locations with reviews"
Expected: List of locations with review counts and ratings
```

## API Endpoints

The chatbot integrates with these backend endpoints:

### Chatbot Endpoints
- `POST /chatbot/chat` - Main chat endpoint
- `GET /chatbot/health` - Health check

### Service Request Endpoints
- `POST /service-requests` - Create request
- `GET /service-requests` - List all requests
- `GET /service-requests/{id}` - Get specific request
- `PATCH /service-requests/{id}/status` - Update status
- `DELETE /service-requests/{id}` - Delete request
- `GET /service-requests/stats/summary` - Get statistics

### Review Endpoints (existing)
- `POST /reviews/reviews` - Create review
- `GET /reviews/reviews` - List all reviews
- `GET /reviews/locations` - List all locations
- More... (see src/backend/routes/reviews.py)

## Troubleshooting

### Error: "Gemini API key not configured"
**Solution:** Add your API key to the `.env` file in `src/backend/`

### Error: "Failed to connect to chatbot service"
**Solution:** 
1. Make sure the backend server is running on port 8000
2. Check that `uvicorn` is running without errors
3. Verify the frontend is trying to connect to `http://localhost:8000`

### Error: Import errors
**Solution:** 
```bash
pip install -e .  # Reinstall dependencies
```

### Chat doesn't respond
**Solution:**
1. Check backend logs for errors
2. Verify Gemini API key is valid
3. Check internet connection (Gemini API requires internet)
4. Look at browser console for JavaScript errors

### Type warnings in IDE
**Solution:** These are expected - Pylance can't fully type pandas/Streamlit. The code will work correctly.

## Data Storage

- Service requests: `src/backend/data/service_requests.parquet`
- Reviews: `src/backend/data/reviews.parquet`
- Locations: `src/backend/data/locations.parquet`

These files are created automatically on first use.

## Security Notes

1. **Never commit your `.env` file** - It contains your API key
2. The `.gitignore` already excludes `.env` files
3. Use environment variables for production deployments
4. Consider implementing rate limiting for production use

## Advanced Configuration

### Changing the AI Model

Edit `.env`:
```env
GEMINI_MODEL=gemini-1.5-pro  # Or another model
```

Available models:
- `gemini-2.0-flash-exp` (default, fastest)
- `gemini-1.5-pro` (more capable)
- `gemini-1.5-flash` (balanced)

### Customizing System Prompts

Edit `src/backend/routes/chatbot.py`:
```python
SYSTEM_INSTRUCTION = """Your custom instructions here..."""
```

### Adding New Functions

To add new chatbot capabilities:

1. Define the function in `chatbot.py`
2. Add it to `function_declarations` list
3. Add it to `FUNCTION_MAP` dictionary
4. The chatbot will automatically be able to use it!

## Support

For issues or questions:
1. Check the logs in both frontend and backend terminals
2. Review the architecture documentation in `docs/CHATBOT_ARCHITECTURE.md`
3. Verify all dependencies are installed correctly

## Next Steps

After setting up:
1. Test all chatbot features
2. Customize system prompts for your needs
3. Add custom functions if needed
4. Consider adding authentication for production
5. Implement rate limiting and monitoring