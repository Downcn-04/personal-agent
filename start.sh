#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Ensure Python is in PATH
export PATH="$HOME/AppData/Local/Programs/Python/Python312:$HOME/AppData/Local/Programs/Python/Python312/Scripts:$PATH"

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "Done."
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "=== Installing backend dependencies ==="
pip install -r "$PROJECT_DIR/backend/requirements.txt" -q

echo "=== Installing frontend dependencies ==="
cd "$PROJECT_DIR/frontend" && npm install --silent

echo "=== Starting backend (port 8000) ==="
cd "$PROJECT_DIR/backend" && uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "=== Starting frontend (port 5173) ==="
cd "$PROJECT_DIR/frontend" && npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both."
echo ""

wait
