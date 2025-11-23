#!/bin/bash

# FocusForge Development Setup Script
echo "🔥 Setting up FocusForge Development Environment..."

# Check if .env exists, create from example if not
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before continuing!"
    echo "   - OpenAI API key for task decomposition"
    echo "   - Spotify credentials for music integration"
    read -p "Press Enter when you've updated the .env file..."
fi

# Check if Hatch is installed
echo "🔍 Checking for Hatch installation..."
if ! command -v hatch &> /dev/null; then
    echo "📦 Installing Hatch for Python project management..."
    pip install hatch
else
    echo "✅ Hatch is already installed"
fi

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is running on http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
else
    echo "❌ Backend API is not responding"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend is not responding"
fi

# Check MongoDB
if docker exec focusforge-mongo mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB is running on localhost:27017"
else
    echo "❌ MongoDB is not responding"
fi

# Check Redis
if docker exec focusforge-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running on localhost:6379"
else
    echo "❌ Redis is not responding"
fi

echo ""
echo "🎉 FocusForge is ready!"
echo ""
echo "🌐 Web App: http://localhost:3000"
echo "🔗 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Development Tips:"
echo "   - Backend (Hatch): cd backend && hatch run dev"
echo "   - Frontend (npm): cd frontend && npm start"  
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo ""
echo "Happy focusing! 🚀"
