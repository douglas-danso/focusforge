# Migration Guide: CLI to Full-Stack Platform

This guide helps you migrate from the CLI-only version of FocusForge to the new full-stack platform with backend APIs, React frontend, and Flutter mobile app.

## What's Changed

### Before (CLI Only)
- Single Python CLI application
- Local file storage
- Manual task entry
- Basic timer functionality

### After (Full-Stack Platform)
- **Backend API** (FastAPI) with comprehensive REST endpoints
- **Web Frontend** (React) with modern, responsive UI
- **Mobile App** (Flutter) for iOS and Android
- **Database** (MongoDB) for persistent data storage
- **Real-time features** with notifications and synchronization
- **Advanced analytics** with charts and insights

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web     │    │  Flutter Mobile │    │   CLI Tool      │
│   Frontend      │    │      App        │    │   (Legacy)      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────── ▼ ──────────┐
                    │     FastAPI Backend    │
                    │    (REST API Server)   │
                    └─────────── ┬ ──────────┘
                                 │
                    ┌─────────── ▼ ──────────┐
                    │       MongoDB          │
                    │     (Database)         │
                    └────────────────────────┘
```

## Step-by-Step Migration

### 1. Backup Your Current Data

If you have existing CLI data, export it first:

```bash
# Using the old CLI
focusforge export-data --output backup.json
```

### 2. Set Up the New Environment

1. **Clone or update your repository**
   ```bash
   git pull origin main  # Get latest changes
   ```

2. **Create environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the new services**
   ```bash
   # Quick setup (Windows)
   setup-dev.bat
   
   # Quick setup (Linux/Mac)
   chmod +x setup-dev.sh
   ./setup-dev.sh
   
   # Manual setup
   docker-compose up -d
   ```

### 3. Access the New Interfaces

- **Web App**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Endpoint**: http://localhost:8000/api/v1

### 4. Import Your Data (If Available)

1. **Via Web Interface**:
   - Go to Settings → Data & Privacy
   - Click "Import Data"
   - Select your backup.json file

2. **Via API** (for developers):
   ```bash
   curl -X POST http://localhost:8000/api/v1/import \
     -H "Content-Type: application/json" \
     -d @backup.json
   ```

## Feature Mapping

### CLI Commands → Web/API Equivalents

| CLI Command | Web Interface | API Endpoint |
|-------------|---------------|--------------|
| `focusforge add "task"` | Tasks → Add Task | `POST /api/v1/tasks` |
| `focusforge mood happy` | Dashboard → Mood Log | `POST /api/v1/mood` |
| `focusforge streak` | Analytics → Current Streak | `GET /api/v1/analytics/streak` |
| `focusforge store` | Store Page | `GET /api/v1/store/items` |
| `focusforge buy "item"` | Store → Purchase | `POST /api/v1/store/purchase/{item}` |
| `focusforge stats` | Analytics Page | `GET /api/v1/analytics` |
| `focusforge play-music` | Pomodoro → Play Music | `POST /api/v1/spotify/play/{uri}` |

### New Features Available

1. **Visual Task Management**
   - Drag-and-drop task organization
   - Visual progress tracking
   - Task breakdown visualization

2. **Advanced Pomodoro Timer**
   - Visual countdown timer
   - Session history
   - Custom durations
   - Break management

3. **Comprehensive Analytics**
   - Interactive charts
   - Mood trend analysis
   - Weekly/monthly patterns
   - Achievement tracking

4. **Enhanced Store System**
   - Visual item browsing
   - Purchase history
   - Point earning tracking
   - Achievement rewards

5. **Mobile Accessibility**
   - Full-featured mobile app
   - Offline capability
   - Push notifications
   - Cross-device sync

## Development Workflow

### For CLI Users Transitioning to API Development

1. **Explore the API**
   ```bash
   # Get all tasks
   curl http://localhost:8000/api/v1/tasks
   
   # Create a task
   curl -X POST http://localhost:8000/api/v1/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "My Task", "duration_minutes": 25}'
   
   # Start a Pomodoro
   curl -X POST http://localhost:8000/api/v1/pomodoro/start \
     -H "Content-Type: application/json" \
     -d '{"task_id": "task_id_here", "duration_minutes": 25}'
   ```

2. **Understand the Data Models**
   
   Check the API documentation at http://localhost:8000/docs for:
   - Request/response schemas
   - Available endpoints
   - Authentication requirements

3. **Extend the System**
   
   Add new features by:
   - Creating new API endpoints in `backend/app/api/v1/endpoints/`
   - Adding corresponding services in `backend/app/services/`
   - Implementing UI components in `frontend/src/components/`

### Database Schema

The new system uses MongoDB with these main collections:

```javascript
// Users
{
  "_id": ObjectId,
  "email": "user@example.com",
  "username": "user123",
  "created_at": ISODate,
  "is_active": true
}

// Tasks  
{
  "_id": ObjectId,
  "user_id": "user_id",
  "title": "Task Title",
  "description": "Description",
  "status": "pending|in_progress|completed",
  "duration_minutes": 25,
  "blocks": ["Block 1", "Block 2"],
  "created_at": ISODate
}

// Pomodoro Sessions
{
  "_id": ObjectId,
  "user_id": "user_id", 
  "task_id": "task_id",
  "duration_minutes": 25,
  "started_at": ISODate,
  "completed_at": ISODate,
  "is_completed": true
}

// Mood Logs
{
  "_id": ObjectId,
  "user_id": "user_id",
  "feeling": "happy",
  "note": "Great day!",
  "timestamp": ISODate
}
```

## Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check Docker is running
   docker --version
   
   # Check ports are available
   netstat -an | grep :8000
   netstat -an | grep :3000
   
   # View service logs
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. **API returns authentication errors**
   - The new system includes user management
   - For development, user_id defaults to "default"
   - Implement proper authentication for production

3. **Frontend can't connect to backend**
   - Check REACT_APP_API_URL in frontend environment
   - Verify CORS settings in backend
   - Ensure both services are running

4. **Database connection issues**
   - Verify MongoDB is running: `docker-compose ps`
   - Check connection string in .env
   - View MongoDB logs: `docker-compose logs mongo`

### Getting Help

1. **Check the logs**
   ```bash
   docker-compose logs -f  # All services
   docker-compose logs backend  # Backend only
   docker-compose logs frontend  # Frontend only
   ```

2. **Reset everything**
   ```bash
   docker-compose down -v  # Stop and remove volumes
   docker-compose up -d    # Start fresh
   ```

3. **Verify your environment**
   ```bash
   # Check your .env file has required variables
   cat .env | grep -E "(OPENAI_API_KEY|MONGODB_URI)"
   ```

## Keeping the CLI (Optional)

The original CLI still works! You can use both:

1. **Install CLI alongside new system**
   ```bash
   cd focusforge
   pip install -e .  # Install CLI in development mode
   focusforge --help  # CLI commands still work
   ```

2. **CLI can use the new backend**
   Update CLI configuration to point to the new API:
   ```python
   # In src/core/settings.py
   API_BASE_URL = "http://localhost:8000/api/v1"
   ```

## Next Steps

1. **Explore the web interface** at http://localhost:3000
2. **Try the API** at http://localhost:8000/docs  
3. **Set up mobile development** (Flutter) for cross-platform access
4. **Customize and extend** the system for your needs
5. **Deploy to production** when ready

## Need Help?

- 📖 **Documentation**: Check the main README.md
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💬 **Discussions**: Ask questions in GitHub Discussions
- 📧 **Email**: Contact support@focusforge.app

Welcome to the new FocusForge! 🎉
