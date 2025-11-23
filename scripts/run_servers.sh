#!/usr/bin/env zsh
# Script to start FastAPI (uvicorn) and Streamlit concurrently.
# Usage: ./scripts/run_servers.sh

set -euo pipefail

# Resolve repository root (one level up from scripts directory)
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)

# Activate virtualenv if present
if [ -f "$REPO_ROOT/venv/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$REPO_ROOT/venv/bin/activate"
fi

# Ensure PYTHONPATH includes src so imports like `backend` work
export PYTHONPATH="$REPO_ROOT/src:${PYTHONPATH:-}"

UVICORN_CMD=(uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload)
STREAMLIT_CMD=(streamlit run src/frontend/main.py --server.port 8509)

PIDS=()

start() {
  name=$1
  shift
  echo "Starting: $name"
  "${@}" &
  PIDS+=("$!")
  echo "$name PID: ${PIDS[-1]}"
}

stop_all() {
  echo "Shutting down servers..."
  for pid in "${PIDS[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
  done
}

# Trap to ensure cleanup on exit
trap 'stop_all; exit' INT TERM EXIT

start "FastAPI (uvicorn)" "${UVICORN_CMD[@]}"
start "Streamlit" "${STREAMLIT_CMD[@]}"

echo "Servers started. FastAPI -> http://127.0.0.1:8000  Streamlit -> http://127.0.0.1:8501"

# Wait for background processes
wait
