#!/bin/bash

echo "🚀 Starting DataMind Forensic Environment..."

# Start FastAPI Backend
echo "📡 Initializing Backend (Port 8000)..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start Vite Frontend
echo "💻 Initializing Frontend (Port 3000)..."
cd frontend && npm run dev -- --port 3000 &
FRONTEND_PID=$!

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

echo "✅ Systems Online."
echo "   - Backend: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:3000"

wait
