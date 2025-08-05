#!/bin/bash

# FocusForge Frontend Service Startup Script

set -e

echo "🌐 Starting FocusForge Frontend Service..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create frontend-specific .env file if it doesn't exist
if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend .env file..."
    cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
REACT_APP_ENV=development
GENERATE_SOURCEMAP=true
CHOKIDAR_USEPOLLING=true
EOF
fi

echo "📋 Frontend Service Configuration:"
echo "   - Frontend Port: 3000"
echo "   - API Backend: ${REACT_APP_API_URL:-http://localhost:8000/api/v1}"
echo "   - WebSocket: ${REACT_APP_WEBSOCKET_URL:-ws://localhost:8000/ws}"

# Check if backend is running (optional)
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend service detected on port 8000"
else
    echo "⚠️  Backend service not detected. Frontend will still start but API calls may fail."
    echo "   To start backend: ./start-backend.sh"
fi

# Start frontend service
echo "🔧 Starting frontend service..."
docker-compose -f docker-compose.frontend.yml up -d

# Wait for service to be ready
echo "⏳ Waiting for frontend to start..."
sleep 10

# Health check
echo "🔍 Checking frontend health..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Frontend is running on http://localhost:3000"
        break
    else
        if [ $attempt -eq $max_attempts ]; then
            echo "❌ Frontend failed to start after $max_attempts attempts"
            echo "📋 Checking logs..."
            docker-compose -f docker-compose.frontend.yml logs frontend
            exit 1
        fi
        echo "⏳ Attempt $attempt/$max_attempts - waiting for frontend..."
        sleep 2
        ((attempt++))
    fi
done

echo ""
echo "🎉 Frontend Service is ready!"
echo ""
echo "🌐 Web Application: http://localhost:3000"
echo ""
echo "📋 Management Commands:"
echo "   View logs: docker-compose -f docker-compose.frontend.yml logs -f"
echo "   Stop service: docker-compose -f docker-compose.frontend.yml down"
echo "   Restart service: docker-compose -f docker-compose.frontend.yml restart"
echo "   Shell access: docker exec -it focusforge-frontend sh"
echo ""
echo "💡 Development Tips:"
echo "   - Hot reload is enabled - changes will reflect immediately"
echo "   - Check browser console for any API connection issues"
echo "   - Ensure backend service is running for full functionality"
echo ""
echo "Happy focusing! 🚀"
