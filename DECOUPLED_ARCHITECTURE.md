# FocusForge Decoupled Architecture Guide

## 🏗️ Architecture Overview

FocusForge now follows a **fully decoupled microservices architecture** where each service (backend, frontend, mobile) can be developed, deployed, and scaled independently.

### Services

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| **Backend API** | 8000 | FastAPI + Python | Core business logic, data processing |
| **Web Frontend** | 3000 | React + Material-UI | Web user interface |
| **Mobile App** | 3001 | Flutter | Cross-platform mobile application |
| **API Gateway** | 80/443 | NGINX | Load balancing, routing, SSL termination |
| **Database** | 27017 | MongoDB | Data persistence |
| **Cache** | 6379 | Redis | Session storage, caching |

## 🚀 Quick Start

### Option 1: Individual Services (Recommended for Development)

```powershell
# Start only what you need:

# Backend development
.\start-backend.ps1

# Frontend development  
.\start-frontend.ps1

# Mobile development
.\start-mobile.ps1
```

### Option 2: Service-Specific Docker Compose

```bash
# Backend + Database + Cache
docker-compose -f docker-compose.backend.yml up -d

# Frontend only
docker-compose -f docker-compose.frontend.yml up -d

# Mobile development environment
docker-compose -f docker-compose.mobile.yml up -d
```

### Option 3: Full Production Stack

```bash
# Complete stack with API Gateway
docker-compose -f docker-compose.prod.yml up -d
```

## 📋 Service Details

### Backend Service (Port 8000)

**Technology Stack:**
- FastAPI (Python web framework)
- MongoDB (document database)
- Redis (caching & sessions)
- Hatch (dependency management)

**Key Features:**
- RESTful API with OpenAPI docs
- WebSocket support for real-time features
- JWT authentication
- Rate limiting
- Health checks
- Automatic API documentation

**Endpoints:**
- `GET /health` - Service health check
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/tasks` - Task management
- `POST /api/v1/pomodoro/start` - Start Pomodoro session
- And many more...

**Environment Configuration:**
```bash
# Required
OPENAI_API_KEY=your-api-key

# Optional  
SPOTIPY_CLIENT_ID=your-spotify-id
MONGODB_URI=mongodb://localhost:27017/focusforge
JWT_SECRET_KEY=your-secret-key
```

### Frontend Service (Port 3000)

**Technology Stack:**
- React 18 (UI framework)
- Material-UI (component library)
- React Router (routing)
- Axios (HTTP client)
- Recharts (data visualization)

**Key Features:**
- Responsive design
- Material Design 3
- Real-time updates via WebSocket
- Progressive Web App (PWA) ready
- Hot reload for development
- Production-optimized builds

**Pages:**
- Dashboard with analytics
- Task management with AI decomposition
- Pomodoro timer with visualizations
- Mood tracking
- Gamified store system
- Analytics and reports

**Environment Configuration:**
```bash
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
```

### Mobile Service (Port 3001)

**Technology Stack:**
- Flutter (cross-platform framework)
- BLoC (state management)
- Material Design 3
- HTTP client for API calls

**Key Features:**
- Native performance
- Cross-platform (iOS, Android, Web)
- Material Design 3 theming
- Offline-first architecture
- Push notifications ready
- Biometric authentication ready

**Development:**
- Flutter web development server on port 3001
- Hot reload enabled
- iOS simulator support (macOS only)
- Android emulator support
- Physical device debugging via USB

## 🔧 Development Workflows

### Backend Development

```bash
# Method 1: Direct Hatch usage
cd backend
hatch run dev  # Start with auto-reload

# Method 2: Docker development
.\start-backend.ps1

# Method 3: Manual Docker
docker-compose -f docker-compose.backend.yml up -d
```

### Frontend Development

```bash
# Method 1: Direct npm usage
cd frontend
npm start

# Method 2: Docker development
.\start-frontend.ps1

# Method 3: Manual Docker  
docker-compose -f docker-compose.frontend.yml up -d
```

### Mobile Development

```bash
# Method 1: Docker Flutter environment
.\start-mobile.ps1

# Method 2: Local Flutter (requires Flutter SDK)
cd mobile
flutter run -d web-server --web-port 3001

# Method 3: Manual Docker
docker-compose -f docker-compose.mobile.yml up -d
```

## 🌐 Production Deployment

### Architecture

```
Internet
    ↓
NGINX API Gateway (Port 80/443)
    ↓
┌─────────────┬─────────────┬─────────────┐
│   Frontend  │   Backend   │   Mobile    │
│   (React)   │  (FastAPI)  │  (Flutter)  │
│   Port 80   │  Port 8000  │  Port 3001  │
└─────────────┴─────────────┴─────────────┘
         ↓
┌─────────────┬─────────────┐
│   MongoDB   │    Redis    │
│  Port 27017 │  Port 6379  │
└─────────────┴─────────────┘
```

### Deployment Commands

```bash
# Full production stack
docker-compose -f docker-compose.prod.yml up -d

# Individual services for scaling
docker-compose -f docker-compose.backend.yml up -d --scale backend=3
docker-compose -f docker-compose.frontend.yml up -d --scale frontend=2
```

### Environment Configuration

Create production environment files:
```bash
cp .env.backend.template .env.backend.prod
cp .env.frontend.template .env.frontend.prod
cp .env.mobile.template .env.mobile.prod

# Edit with production values
```

## 🔒 Security Features

### API Gateway (NGINX)
- Rate limiting (10 requests/second for API, 5 for auth)
- SSL termination
- Security headers (XSS, CSRF protection)
- CORS configuration
- Request/response logging

### Backend Security
- JWT authentication
- Password hashing
- Input validation
- SQL injection prevention (using MongoDB)
- Environment variable protection

### Network Security
- Internal networks for database communication
- Service isolation
- Health check endpoints
- Container security scanning ready

## 📊 Monitoring & Logging

### Health Checks
```bash
# Backend
curl http://localhost:8000/health

# Frontend  
curl http://localhost:3000/health

# Via API Gateway
curl http://localhost/health
```

### Service Logs
```bash
# Individual services
docker-compose -f docker-compose.backend.yml logs -f backend
docker-compose -f docker-compose.frontend.yml logs -f frontend
docker-compose -f docker-compose.mobile.yml logs -f mobile-dev

# Production stack
docker-compose -f docker-compose.prod.yml logs -f
```

### Container Stats
```bash
docker stats focusforge-backend focusforge-frontend focusforge-mongo focusforge-redis
```

## 🔄 CI/CD Pipeline Ready

Each service can have independent CI/CD pipelines:

### Backend Pipeline
```yaml
# .github/workflows/backend.yml
- Test backend code
- Build Docker image
- Deploy to staging
- Run integration tests
- Deploy to production
```

### Frontend Pipeline
```yaml
# .github/workflows/frontend.yml
- Test React components
- Build production bundle
- Deploy to CDN
- Run E2E tests
```

### Mobile Pipeline
```yaml
# .github/workflows/mobile.yml
- Test Flutter code
- Build APK/IPA
- Deploy to app stores
- Run device tests
```

## 🚀 Scaling Strategies

### Horizontal Scaling
```bash
# Scale backend instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=5

# Scale frontend instances
docker-compose -f docker-compose.prod.yml up -d --scale frontend=3
```

### Load Balancing
- NGINX automatically load balances between instances
- Least connections algorithm
- Health check integration
- Failover support

### Database Scaling
- MongoDB replica sets
- Sharding for large datasets
- Read replicas for analytics
- Redis clustering for cache

## 📝 Migration from Monolithic Setup

If you're upgrading from the previous monolithic setup:

1. **Backup your data:**
   ```bash
   docker exec focusforge-mongo mongodump --out /tmp/backup
   ```

2. **Stop old services:**
   ```bash
   docker-compose down
   ```

3. **Start new decoupled services:**
   ```bash
   .\start-backend.ps1
   .\start-frontend.ps1
   ```

4. **Verify migration:**
   - Check http://localhost:8000/health
   - Check http://localhost:3000
   - Test API functionality

## 🛠️ Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check Docker
docker --version
docker info

# Check ports
netstat -an | findstr ":8000"
netstat -an | findstr ":3000"
```

**API connection errors:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in backend
- Verify environment variables in frontend

**Database connection issues:**
```bash
# Check MongoDB
docker exec focusforge-mongo mongosh --eval "db.adminCommand('ping')"

# Check Redis
docker exec focusforge-redis redis-cli ping
```

**Performance issues:**
```bash
# Monitor resources
docker stats

# Check logs for errors
docker-compose logs --tail=100
```

### Getting Help

1. **Check service logs:**
   ```bash
   .\start-backend.ps1    # Includes health checks
   .\start-frontend.ps1   # Includes health checks
   ```

2. **Verify configuration:**
   ```bash
   # Check environment files
   Get-Content .env.backend.template
   Get-Content .env.frontend.template
   ```

3. **Reset everything:**
   ```bash
   # Stop all services
   docker-compose -f docker-compose.backend.yml down -v
   docker-compose -f docker-compose.frontend.yml down -v
   docker-compose -f docker-compose.mobile.yml down -v
   
   # Start fresh
   .\start-backend.ps1
   .\start-frontend.ps1
   ```

## 📚 Additional Resources

- [Backend API Documentation](http://localhost:8000/docs) (when running)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Flutter Documentation](https://flutter.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

**Happy coding with your decoupled FocusForge architecture! 🚀**
