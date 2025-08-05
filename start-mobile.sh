#!/bin/bash

# FocusForge Mobile Service Startup Script

set -e

echo "📱 Starting FocusForge Mobile Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create mobile-specific environment file if it doesn't exist
if [ ! -f mobile/.env ]; then
    echo "📝 Creating mobile .env file..."
    cat > mobile/.env << EOF
FLUTTER_API_URL=http://localhost:8000/api/v1
FLUTTER_WEBSOCKET_URL=ws://localhost:8000/ws
FLUTTER_ENV=development
EOF
fi

echo "📋 Mobile Service Configuration:"
echo "   - Flutter Web Dev: http://localhost:3001"
echo "   - Flutter Build Server: http://localhost:8080"
echo "   - API Backend: ${FLUTTER_API_URL:-http://localhost:8000/api/v1}"

# Check if backend is running (optional)
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend service detected on port 8000"
else
    echo "⚠️  Backend service not detected. Mobile app will still start but API calls may fail."
    echo "   To start backend: ./start-backend.sh"
fi

# Start mobile development environment
echo "🔧 Starting mobile development environment..."
docker-compose -f docker-compose.mobile.yml up -d

# Wait for service to be ready
echo "⏳ Waiting for Flutter environment to start..."
sleep 20

# Health check
echo "🔍 Checking mobile development environment..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:3001 > /dev/null; then
        echo "✅ Flutter web development server is running on http://localhost:3001"
        break
    else
        if [ $attempt -eq $max_attempts ]; then
            echo "❌ Flutter development environment failed to start after $max_attempts attempts"
            echo "📋 Checking logs..."
            docker-compose -f docker-compose.mobile.yml logs mobile-dev
            exit 1
        fi
        echo "⏳ Attempt $attempt/$max_attempts - waiting for Flutter..."
        sleep 3
        ((attempt++))
    fi
done

echo ""
echo "🎉 Mobile Development Environment is ready!"
echo ""
echo "📱 Flutter Web App: http://localhost:3001"
echo "🔧 Flutter Build Server: http://localhost:8080"
echo ""
echo "📋 Management Commands:"
echo "   View logs: docker-compose -f docker-compose.mobile.yml logs -f"
echo "   Stop service: docker-compose -f docker-compose.mobile.yml down"
echo "   Restart service: docker-compose -f docker-compose.mobile.yml restart"
echo "   Flutter shell: docker exec -it focusforge-mobile-dev bash"
echo ""
echo "💡 Development Tips:"
echo "   - Use http://localhost:3001 for web development"
echo "   - Connect physical devices via USB debugging"
echo "   - Use Android Studio/VS Code Flutter extensions for better IDE support"
echo "   - Hot reload is available for faster development"
echo ""
echo "📱 Device Options:"
echo "   - Web: Already running on port 3001"
echo "   - Android: Connect device and run 'flutter run' in container"
echo "   - iOS: Requires macOS host with Xcode"
echo ""
echo "Happy mobile development! 🚀"
