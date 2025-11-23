# Troubleshooting Guide

## Error: "Gemini API key not configured"

### Symptoms
```
Error: 500 - {"detail":"Chat error: 500: Gemini API key not configured. Please set GEMINI_API_KEY environment variable."}
```

### Solution

**Step 1: Verify your .env file**

Make sure `src/backend/.env` exists and contains:
```env
GEMINI_API_KEY="your_actual_api_key_here"
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Step 2: Restart the backend server**

This is the most important step! The server needs to be restarted to pick up environment variable changes.

```bash
# Stop the backend server (Ctrl+C in the terminal running it)

# Then restart it:
cd src/backend
uvicorn backend.main:app --reload --port 8000
```

**Step 3: Verify the configuration**

Check that the API key is loaded by visiting:
```
http://localhost:8000/chatbot/health
```

You should see:
```json
{
  "status": "healthy",
  "gemini_configured": true,
  "model": "gemini-2.0-flash-exp"
}
```

If `gemini_configured` is `false`, the API key is not being loaded.

### Common Causes

1. **Backend server not restarted** - Most common! Always restart after changing .env
2. **Wrong .env location** - Must be in `src/backend/.env`
3. **Typo in environment variable name** - Must be exactly `GEMINI_API_KEY`
4. **Quotes issue** - Use `GEMINI_API_KEY="your_key"` or `GEMINI_API_KEY=your_key` (both work)

## Other Common Issues

### Import Error: "No module named 'google.generativeai'"

**Solution:**
```bash
pip install -e .
# OR
pip install google-generativeai
```

### Error: "Failed to connect to chatbot service"

**Solution:**
1. Check backend is running on port 8000
2. Check logs in backend terminal for errors
3. Try accessing http://localhost:8000/docs to verify backend is running

### Chat doesn't respond / Loading forever

**Possible causes:**
1. Invalid API key - Check the key at https://makersuite.google.com/app/apikey
2. No internet connection - Gemini API requires internet
3. Rate limiting - Wait a few moments and try again
4. Model not available - Try changing `GEMINI_MODEL` to `gemini-1.5-pro`

### Type errors in IDE (Pylance warnings)

**These are normal!** Pylance can't fully type pandas/Streamlit dynamic features. The code will work correctly despite the warnings.

## Quick Verification Checklist

- [ ] `.env` file exists at `src/backend/.env`
- [ ] `GEMINI_API_KEY` is set in `.env`
- [ ] Backend server has been **restarted** after adding the key
- [ ] `/chatbot/health` shows `gemini_configured: true`
- [ ] Internet connection is working
- [ ] Dependencies are installed (`pip install -e .`)

## Still Having Issues?

1. Check backend terminal for error logs
2. Check frontend terminal for connection errors
3. Verify API key is valid at https://makersuite.google.com/app/apikey
4. Try a simple test: visit http://localhost:8000/docs and test `/chatbot/health`