# AI Chatbot Quick Start

## Setup (2 minutes)

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Add your Gemini API key:**
   ```bash
   cd src/backend
   cp .env.example .env
   # Edit .env and add your API key to GEMINI_API_KEY
   ```

3. **Start the servers:**
   ```bash
   # From project root
   ./scripts/run_servers.sh
   
   # OR manually:
   # Terminal 1: cd src/backend && uvicorn backend.main:app --reload
   # Terminal 2: cd src/frontend && streamlit run main.py
   ```

4. **Access the chatbot:**
   - Open http://localhost:8501
   - Click "AI Assistant" button

## Example Prompts

### Service Request
```
I need a wheelchair ramp at 100 Main St, Boston. 
Coordinates: 42.3601, -71.0589. High priority. 
My name is John Doe. The entrance has 3 steps with no ramp.
```

### Submit Review
```
Create a review for Boston Common. 
Location ID: boston_common, coordinates: 42.3551, -71.0656.
Title: "Excellent accessibility"
Content: "Wide paved paths, accessible restrooms, benches available"
Rating: 5, Author: Jane Smith
```

### Search
```
Show me accessible locations near downtown Boston
```

## That's it! 🎉

The chatbot will:
- ✅ Answer questions about accessibility
- ✅ Create service requests automatically
- ✅ Submit reviews for you
- ✅ Search location data
- ✅ Maintain conversation context

For detailed documentation, see `docs/CHATBOT_SETUP.md`