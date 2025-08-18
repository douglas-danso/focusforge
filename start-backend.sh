#!/bin/bash

# FocusForge Backend Service Startup Script

set -e

echo "🚀 Starting FocusForge Backend Service..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding."
    read -p "Press Enter to continue..."
fi

# Source environment variables
source .env

# Check required environment variables
required_vars=("OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

echo "📋 Backend Service Configuration:"
echo "   - API Port: 8000"
echo "   - Database: MongoDB (localhost:27017)"
echo "   - Cache: Redis (localhost:6379)"
echo "   - Environment: ${DATABASE_NAME:-focusforge}"

# Start backend services
echo "🔧 Starting backend infrastructure..."
docker compose -f docker-compose.backend.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Health check
echo "🔍 Checking service health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is running on http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo "📊 Interactive API: http://localhost:8000/redoc"
else
    echo "❌ Backend API is not responding"
    echo "📋 Checking logs..."
    docker compose -f docker-compose.backend.yml logs backend
    exit 1
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
echo "🎉 Backend Service is ready!"
echo ""
echo "📋 Management Commands:"
echo "   View logs: docker compose -f docker-compose.backend.yml logs -f"
echo "   Stop service: docker compose -f docker-compose.backend.yml down"
echo "   Restart service: docker compose -f docker-compose.backend.yml restart"
echo "   Database shell: docker exec -it focusforge-mongo mongosh focusforge"
echo "   Redis CLI: docker exec -it focusforge-redis redis-cli"
echo ""
echo "Happy coding! 🚀"
