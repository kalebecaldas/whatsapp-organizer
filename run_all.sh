#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting WhatsApp Organizer...${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    if port_in_use $1; then
        echo -e "${YELLOW}⚠️  Port $1 is in use. Killing process...${NC}"
        lsof -ti :$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to check if a process is running by name
process_running() {
    pgrep -f "$1" >/dev/null 2>&1
}

# Function to kill process by name
kill_process() {
    if process_running "$1"; then
        echo -e "${YELLOW}⚠️  Process $1 is running. Killing it...${NC}"
        pkill -f "$1" 2>/dev/null || true
        sleep 2
    fi
}

# Check and install Python dependencies
echo -e "${BLUE}📦 Checking Python dependencies...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}✅ Virtual environment found${NC}"
source venv/bin/activate

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
cd backend
pip install -r requirements.txt 2>/dev/null || {
    echo -e "${YELLOW}⚠️  requirements.txt not found. Installing basic dependencies...${NC}"
    pip install flask flask-cors flask-socketio python-dotenv openai redis
}
cd ..

# Check OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    # Try to load from .env file
    if [ -f "backend/.env" ]; then
        echo -e "${BLUE}📄 Loading OpenAI API key from .env file...${NC}"
        export OPENAI_API_KEY=$(grep "OPENAI_API_KEY=" backend/.env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        if [ ! -z "$OPENAI_API_KEY" ]; then
            echo -e "${GREEN}✅ OpenAI API key loaded from .env${NC}"
        else
            echo -e "${YELLOW}⚠️  OPENAI_API_KEY not found in .env file${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  OPENAI_API_KEY not set and .env file not found${NC}"
        echo -e "${BLUE}💡 You can set it with: export OPENAI_API_KEY='your-api-key-here'${NC}"
        echo -e "${BLUE}💡 Or create a .env file in the backend directory${NC}"
    fi
fi

# Kill existing processes
echo -e "${BLUE}🧹 Cleaning up existing processes...${NC}"
kill_port 5001
kill_port 3001
kill_process "node.*bot.js"
kill_process "python.*app.py"

# Start backend
echo -e "${BLUE}🚀 Starting backend (Flask) on port 5001...${NC}"

# Set OpenAI API key if available
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✅ OpenAI API key loaded${NC}"
    export OPENAI_API_KEY="$OPENAI_API_KEY"
fi

# Start backend in background from root directory
python3 backend/app.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Backend started with PID: $BACKEND_PID${NC}"
    
    # Wait for backend to be ready
    echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:5001/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend is up!${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Backend failed to start properly${NC}"
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
        sleep 1
    done
else
    echo -e "${RED}❌ Failed to start backend${NC}"
    exit 1
fi

# Check if Venom Bot is already running
echo -e "${BLUE}🤖 Checking Venom Bot status...${NC}"
if process_running "node.*bot.js"; then
    echo -e "${GREEN}✅ Venom Bot is already running${NC}"
    VENOM_PID=$(pgrep -f "node.*bot.js")
    echo -e "${BLUE}📋 Venom Bot PID: $VENOM_PID${NC}"
else
    # Start Venom Bot
    echo -e "${BLUE}🤖 Starting Venom Bot for WhatsApp integration...${NC}"
    if [ -d "backend/venom-bot-flask" ]; then
        cd backend/venom-bot-flask
        
        # Check if node_modules exists, if not install dependencies
        if [ ! -d "node_modules" ]; then
            echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
            npm install >/dev/null 2>&1 || true
        fi
        
        # Start Venom Bot in background
        node bot.js > ../../venom.log 2>&1 &
        VENOM_PID=$!
        cd ../..
        
        # Wait a moment for Venom Bot to start
        sleep 5
        
        # Check if Venom Bot started successfully
        if kill -0 $VENOM_PID 2>/dev/null; then
            echo -e "${GREEN}✅ Venom Bot started with PID: $VENOM_PID${NC}"
        else
            echo -e "${RED}❌ Venom Bot did not start correctly. Check venom.log.${NC}"
            VENOM_PID=""
        fi
    else
        echo -e "${YELLOW}⚠️  Venom Bot directory not found. Skipping...${NC}"
        VENOM_PID=""
    fi
fi

# Start frontend
echo -e "${BLUE}🌐 Starting frontend (React) on port 3001...${NC}"
cd finalfrontend

# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
    npm install >/dev/null 2>&1 || true
fi

# Start frontend in background
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Frontend started with PID: $FRONTEND_PID${NC}"
else
    echo -e "${RED}❌ Failed to start frontend${NC}"
fi

echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo -e "${BLUE}📱 Frontend: http://localhost:3001${NC}"
echo -e "${BLUE}🔧 Backend: http://localhost:5001${NC}"
echo -e "${BLUE}📊 Health check: http://localhost:5001/health${NC}"
if [ ! -z "$VENOM_PID" ]; then
    echo -e "${BLUE}🤖 Venom Bot: Running (PID: $VENOM_PID)${NC}"
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down all services...${NC}"
    
    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    
    # Kill Venom Bot
    if [ ! -z "$VENOM_PID" ]; then
        kill $VENOM_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Venom Bot stopped${NC}"
    fi
    
    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
    
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo -e "${BLUE}💡 Press Ctrl+C to stop services${NC}"

# Keep script running
wait 