#!/bin/bash

# FocusForge Production Backend Service Startup Script
# Handles replica sets, monitoring, and proper service orchestration

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo "🚀 Starting FocusForge Production Backend Service..."

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    log_error "Docker is not running. Please start Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    log_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Determine compose command and file
COMPOSE_FILE="docker-compose.backend.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "Docker Compose file '$COMPOSE_FILE' not found"
    exit 1
fi

if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose -f $COMPOSE_FILE"
else
    COMPOSE_CMD="docker-compose -f $COMPOSE_FILE"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    log_warning "Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        log_warning "Please edit .env file with your configuration before proceeding."
        read -p "Press Enter after editing .env file..."
    else
        log_error ".env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

# Source environment variables
source .env

# Check required environment variables
required_vars=("OPENAI_API_KEY")
optional_vars=("JWT_SECRET_KEY" "GOOGLE_CLIENT_ID" "GOOGLE_CLIENT_SECRET")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        log_error "Required environment variable $var is not set in .env file"
        exit 1
    fi
done

# Generate missing optional variables
for var in "${optional_vars[@]}"; do
    if [ -z "${!var}" ]; then
        case $var in
            "JWT_SECRET_KEY")
                generated_value=$(openssl rand -hex 32 2>/dev/null || echo "fallback-secret-key-$(date +%s)")
                echo "$var=$generated_value" >> .env
                export $var="$generated_value"
                log_warning "$var was missing - generated and added to .env file"
                ;;
            "GOOGLE_CLIENT_ID"|"GOOGLE_CLIENT_SECRET")
                log_warning "$var is not set - Google OAuth will be disabled"
                ;;
        esac
    fi
done

log_info "Backend Service Configuration:"
echo "   - Load Balancer: http://localhost:8004 (HTTP), https://localhost:8443 (HTTPS)"
echo "   - Backend Instances: 2 (Load Balanced)"
echo "   - Database: MongoDB Replica Set (Primary: 27017, Secondary: 27018)"
echo "   - Cache: Redis Master-Slave (Master: 6379, Slave: 6380)"
echo "   - Monitoring: Grafana (http://localhost:3001), Prometheus (http://localhost:9090)"
echo "   - Environment: ${DATABASE_NAME:-focusforge}"

# Clean up any existing containers
log_info "Cleaning up existing containers..."
$COMPOSE_CMD down -v --remove-orphans 2>/dev/null || true

# Start infrastructure services first
log_info "Starting database and cache infrastructure..."
$COMPOSE_CMD up -d mongo-primary mongo-secondary redis-master redis-slave

# Wait for MongoDB instances to be ready
log_info "Waiting for MongoDB instances to start..."
max_attempts=30
attempt=1

check_mongo() {
    docker exec focusforge-mongo-primary mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1
}

while [ $attempt -le $max_attempts ]; do
    if check_mongo; then
        log_success "MongoDB instances are ready"
        break
    fi
    echo -n "."
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    log_error "MongoDB instances failed to start within timeout"
    $COMPOSE_CMD logs mongo-primary mongo-secondary
    exit 1
fi

# Initialize MongoDB replica set
log_info "Initializing MongoDB replica set..."
$COMPOSE_CMD up mongo-setup

# Wait for replica set to be ready
log_info "Waiting for MongoDB replica set to be ready..."
sleep 10

# Verify replica set status
log_info "Checking replica set status and triggering primary election if needed..."

replica_status=$(docker exec focusforge-mongo-primary mongosh --quiet --eval "
try {
    const status = rs.status();
    const primary = status.members.find(m => m.stateStr === 'PRIMARY');
    if (primary) {
        print('ready');
    } else {
        // Force primary election by stepping down any existing primary and reconfiguring
        try { rs.stepDown(0, 0); } catch(e) {}
        // Reconfigure to force election
        const config = rs.conf();
        config.version++;
        rs.reconfig(config, {force: true});
        // Wait a bit and check again
        sleep(5000);
        const newStatus = rs.status();
        const newPrimary = newStatus.members.find(m => m.stateStr === 'PRIMARY');
        print(newPrimary ? 'ready' : 'no-primary');
    }
} catch(e) {
    print('error: ' + e.message);
}
" 2>/dev/null || echo "error")

if [ "$replica_status" = "ready" ]; then
    log_success "MongoDB replica set is ready with primary node"
elif [ "$replica_status" = "no-primary" ]; then
    log_warning "No primary found, attempting to force primary election..."
    # Force one node to become primary
    docker exec focusforge-mongo-primary mongosh --eval "
    try {
        const config = rs.conf();
        config.members[0].priority = 10;  // Make primary have highest priority
        config.members[1].priority = 1;
        config.version++;
        rs.reconfig(config, {force: true});
        print('Reconfigured replica set with priorities');
    } catch(e) {
        print('Reconfig error: ' + e.message);
    }
    " >/dev/null 2>&1
    
    # Wait for election
    sleep 10
    
    # Check final status
    final_status=$(docker exec focusforge-mongo-primary mongosh --quiet --eval "
    try {
        const status = rs.status();
        const primary = status.members.find(m => m.stateStr === 'PRIMARY');
        print(primary ? 'ready' : 'failed');
    } catch(e) {
        print('failed');
    }
    " 2>/dev/null || echo "failed")
    
    if [ "$final_status" = "ready" ]; then
        log_success "MongoDB replica set primary election successful"
    else
        log_warning "MongoDB replica set may take longer to elect primary, continuing..."
    fi
else
    log_warning "MongoDB replica set status unclear, continuing with startup..."
fi

# Start remaining services
log_info "Starting backend application and monitoring services..."
$COMPOSE_CMD up -d

# Wait for services to be ready
log_info "Waiting for all services to start..."
sleep 20

# Health checks
log_info "Performing health checks..."

# Check backend health
backend_health() {
    curl -sf http://localhost:8004/health >/dev/null 2>&1
}

max_attempts=15
attempt=1
while [ $attempt -le $max_attempts ]; do
    if backend_health; then
        log_success "Backend API is responding"
        break
    fi
    echo -n "."
    sleep 3
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    log_error "Backend API health check failed"
    log_info "Checking backend logs..."
    $COMPOSE_CMD logs --tail=20 backend-1 backend-2
    exit 1
fi

# Check individual services
services_status=""

# MongoDB
if docker exec focusforge-mongo-primary mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
    log_success "MongoDB Primary is healthy (localhost:27017)"
    services_status+="✅ MongoDB Primary\n"
else
    log_error "MongoDB Primary is not responding"
    services_status+="❌ MongoDB Primary\n"
fi

# Redis
if docker exec focusforge-redis-master redis-cli ping >/dev/null 2>&1; then
    log_success "Redis Master is healthy (localhost:6379)"
    services_status+="✅ Redis Master\n"
else
    log_error "Redis Master is not responding"
    services_status+="❌ Redis Master\n"
fi

# Prometheus
if curl -sf http://localhost:9090/-/healthy >/dev/null 2>&1; then
    log_success "Prometheus is healthy (localhost:9090)"
    services_status+="✅ Prometheus\n"
else
    log_warning "Prometheus is not responding"
    services_status+="⚠️  Prometheus\n"
fi

# Grafana
if curl -sf http://localhost:3001/api/health >/dev/null 2>&1; then
    log_success "Grafana is healthy (localhost:3001)"
    services_status+="✅ Grafana\n"
else
    log_warning "Grafana is not responding"
    services_status+="⚠️  Grafana\n"
fi

echo ""
log_success "FocusForge Production Backend is ready!"
echo ""
echo -e "${BLUE}📋 Service Endpoints:${NC}"
echo "   🌐 API Gateway (Load Balanced): http://localhost:8004"
echo "   🔒 API Gateway (HTTPS): https://localhost:8443"
echo "   📚 API Documentation: http://localhost:8004/docs"
echo "   📊 Interactive API: http://localhost:8004/redoc"
echo "   📈 Monitoring Dashboard: http://localhost:3001 (admin/admin)"
echo "   📊 Metrics: http://localhost:9090"
echo ""
echo -e "${BLUE}🏗️  Infrastructure:${NC}"
echo "   💾 MongoDB Primary: localhost:27017"
echo "   💾 MongoDB Secondary: localhost:27018"
echo "   🔄 Redis Master: localhost:6379"
echo "   🔄 Redis Slave: localhost:6380"
echo ""
echo -e "${BLUE}📊 Service Status:${NC}"
echo -e "$services_status"
echo ""
echo -e "${BLUE}🛠️  Management Commands:${NC}"
echo "   View all logs:       $COMPOSE_CMD logs -f"
echo "   View backend logs:   $COMPOSE_CMD logs -f backend-1 backend-2"
echo "   Stop all services:   $COMPOSE_CMD down"
echo "   Stop with cleanup:   $COMPOSE_CMD down -v"
echo "   Restart service:     $COMPOSE_CMD restart [service-name]"
echo "   Scale backends:      $COMPOSE_CMD up -d --scale backend-1=3"
echo ""
echo -e "${BLUE}🔧 Database Management:${NC}"
echo "   MongoDB shell:       docker exec -it focusforge-mongo-primary mongosh ${DATABASE_NAME:-focusforge}"
echo "   Redis CLI (master):  docker exec -it focusforge-redis-master redis-cli"
echo "   Check replica set:   docker exec focusforge-mongo-primary mongosh --eval 'rs.status()'"
echo ""
echo -e "${BLUE}📊 Monitoring:${NC}"
echo "   Service metrics:     curl http://localhost:8004/metrics"
echo "   Health status:       curl http://localhost:8004/health"
echo ""
echo -e "${GREEN}🎉 Happy coding! 🚀${NC}"