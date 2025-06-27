#!/bin/bash

echo "🚀 WhatsApp Organizer - Status Report"
echo "======================================"
echo ""

# Check Backend
echo "📊 Backend (Flask):"
if lsof -i :5001 > /dev/null 2>&1; then
    echo "   ✅ Running on http://localhost:5001"
    echo "   📝 Recent logs:"
    tail -3 backend.log 2>/dev/null | sed 's/^/      /'
else
    echo "   ❌ Not running"
fi
echo ""

# Check Frontend
echo "🌐 Frontend (Vite):"
FRONTEND_PORT=$(lsof -i -P | grep LISTEN | grep node | grep -v "3000\|3001" | head -1 | awk '{print $9}' | cut -d: -f2)
if [ ! -z "$FRONTEND_PORT" ]; then
    echo "   ✅ Running on http://localhost:$FRONTEND_PORT"
    echo "   📝 Recent logs:"
    tail -3 frontend.log 2>/dev/null | sed 's/^/      /'
else
    echo "   ❌ Not running"
fi
echo ""

# Check Venom Bot
echo "🤖 Venom Bot Test:"
if pgrep -f "bot-simple.js" > /dev/null; then
    echo "   ✅ Running (Test Mode)"
    echo "   📝 Recent logs:"
    tail -3 venom.log 2>/dev/null | sed 's/^/      /'
else
    echo "   ❌ Not running"
fi
echo ""

# Show API endpoints
echo "🔗 Available Endpoints:"
echo "   • Backend API: http://localhost:5001"
echo "   • Webhook: http://localhost:5001/webhook"
echo "   • Stats: http://localhost:5001/api/stats"
echo "   • Frontend: http://localhost:$FRONTEND_PORT"
echo ""

# Show log files
echo "📝 Log Files:"
echo "   • Backend: backend.log"
echo "   • Frontend: frontend.log"
echo "   • Venom Bot: venom.log"
echo ""

echo "🎉 System is ready for WhatsApp message testing!" 