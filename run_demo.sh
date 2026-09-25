#!/usr/bin/env bash
set -e

echo "=================================================="
echo "🎯 Launching CareerLens: AI-Powered Career Platform"
echo "=================================================="

# Check and activate backend venv
if [ -d "backend/venv" ]; then
    echo "Starting FastAPI backend on http://127.0.0.1:8000..."
    backend/venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 &
    BACKEND_PID=$!
else
    echo "Backend venv not found. Please run: cd backend && python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Start frontend
echo "Starting React/Vite frontend on http://localhost:3000..."
cd frontend
npm run dev -- --host 127.0.0.1 --port 3000 &
FRONTEND_PID=$!
cd ..

# Wait for backend to be ready
echo "Waiting for backend service to be ready..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
        echo "✅ Backend is healthy on http://127.0.0.1:8000"
        break
    fi
    sleep 0.5
done

cleanup() {
    echo ""
    echo "Shutting down CareerLens services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

echo ""
echo "🚀 CareerLens is LIVE!"
echo "👉 Frontend: http://localhost:3000"
echo "👉 Backend API Docs: http://127.0.0.1:8000/docs"
echo "Press Ctrl+C to stop all services."
echo ""

wait
