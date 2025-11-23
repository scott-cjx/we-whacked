# Run servers

This script starts the FastAPI backend (via `uvicorn`) and the Streamlit frontend concurrently.

Prerequisites:
- A Python virtual environment with project dependencies installed (optional but recommended).
- `uvicorn` and `streamlit` available in the active environment (e.g. `pip install -r src/backend/requirements.txt` and `pip install streamlit`).

Usage:

Make the script executable (one-time):

```bash
chmod +x scripts/run_servers.sh
```

Run the script:

```bash
./scripts/run_servers.sh
```

The script will:
- activate `venv` if `./venv/bin/activate` exists
- export `PYTHONPATH=./src` so `backend` imports work
- start FastAPI at `http://127.0.0.1:8000` and Streamlit at `http://127.0.0.1:8501`

To stop the servers, press Ctrl+C in the terminal running the script.
