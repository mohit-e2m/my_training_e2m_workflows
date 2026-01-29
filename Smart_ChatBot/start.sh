#!/bin/bash

# Smart Chatbot Startup Script
# Runs both backend and frontend servers

echo "🚀 Starting Smart Chatbot..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Kill any existing processes on ports 5000 and 8000
echo "🧹 Cleaning up existing processes..."
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 1

# Start backend
echo ""
echo -e "${BLUE}📡 Starting Backend Server (Port 5000)...${NC}"
cd backend
source venv/bin/activate
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to initialize
sleep 3

# Start frontend
echo ""
echo -e "${BLUE}🌐 Starting Frontend Server (Port 8000)...${NC}"
cd frontend
python3 server.py &
FRONTEND_PID=$!
cd ..

# Wait a moment for servers to start
sleep 2

echo ""
echo -e "${GREEN}✅ Smart Chatbot is running!${NC}"
echo ""
echo "📱 Main Application: http://localhost:8000/index.html"
echo "⚙️  Admin Dashboard:  http://localhost:8000/admin.html"
echo "🔌 Backend API:       http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Keep script running
wait
