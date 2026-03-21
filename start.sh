#!/bin/bash
# VidyāMitra — Quick Start Script
# Run from the project root: ./start.sh

set -e

echo "🙏 VidyāMitra — The Renaissance Edition"
echo "========================================="

# ── Check Python ──────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 not found. Please install Python 3.11+"
  exit 1
fi

# ── Backend Setup ─────────────────────────
echo ""
echo "📦 Setting up backend..."
cd backend

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️  Created .env from .env.example"
  echo "   → Please add your GROQ_API_KEY to backend/.env"
fi

if [ ! -d "venv" ]; then
  echo "🐍 Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q

echo "✅ Backend dependencies installed"
echo ""
echo "🚀 Starting FastAPI backend on http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo ""

# Start backend in background
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# ── Frontend ──────────────────────────────
cd ../frontend
echo "🌐 Starting frontend on http://localhost:3000"
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "✅ VidyāMitra is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers."

# Wait and cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
