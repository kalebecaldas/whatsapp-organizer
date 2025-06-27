#!/bin/bash

echo "🧪 WhatsApp Message Simulation Test"
echo "=================================="

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:5001/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running. Starting backend..."
    cd backend
    source ../venv/bin/activate
    export OPENAI_API_KEY=$(tail -1 "chave open ai api.txt" | sed 's/^OPENAI //')
    python3 app.py &
    BACKEND_PID=$!
    echo "✅ Backend started with PID: $BACKEND_PID"
    sleep 3
    cd ..
fi

echo ""
echo "🚀 Starting test simulation..."
echo ""

# Run the test script
cd backend
python3 test_webhook.py

echo ""
echo "🎉 Test completed!"
echo "Check the frontend at http://localhost:3001 to see if messages appear" 