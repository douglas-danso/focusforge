# FocusForge 🔥

A comprehensive productivity and focus management platform powered by the **Memory-Chain-Planner** architecture with AI-driven task decomposition, intelligent planning, and adaptive memory systems.

## Architecture

FocusForge implements the advanced **Memory-Chain-Planner** pattern:

```
[ Mobile / Web Frontend ]
         ↕ (REST / WebSocket)
[ FastAPI API Gateway ]  ←→  [ Memory-Chain-Planner Orchestrator ]
         ↕                            ↕
[ Memory Layer ]  ←→  [ Chains Layer ]  ←→  [ Planner Layer ]
         ↕                            ↕                ↕
[ Unified MCP System (Adapter Layer) ]  ←→  [ Background Tasks (RQ) ]
         ↕
[ External Services: MongoDB, Redis, Spotify, Calendar ]
```

### Core Components:

- **🧠 Memory Layer** - Multi-type memory system with LangChain compatibility
- **🔗 Chains Layer** - Specialized LangChain workflows for task processing
- **� Planner Layer** - Intelligent action planning and coordination
- **🔄 Orchestrator** - Central coordinator implementing complete workflows
- **⚡ Background Tasks** - RQ/Redis-based async processing
- **🔧 Unified MCP System** - 15+ productivity tools with consistent interface
- **🌐 Frontend Apps** - React web and Flutter mobile applications
- **� Persistence** - MongoDB with Redis caching

**Key Features:**
- **Memory-aware processing** with context persistence
- **AI-driven chain execution** for complex workflows
- **Intelligent action planning** with dependency management
- **Background processing** for long-running tasks
- **Unified tool interface** for consistent AI agent integration

## Features ✨

### Core Functionality
- 🧠 **Memory-Chain-Planner** - Advanced AI architecture with memory persistence
- 🔗 **Intelligent Chains** - AI-powered task analysis and decomposition
- 🎯 **Smart Planning** - Dependency-aware action planning and execution
- 🍅 **Enhanced Pomodoro** - AI-optimized focus sessions with ritual recommendations
- 📝 **Task Management** - Memory-aware task creation and completion workflows
- 📊 **Analytics & Insights** - Pattern recognition and productivity optimization
- 🏪 **Reward Store** - Gamified rewards with intelligent recommendations
- 😊 **Mood Tracking** - Emotional pattern analysis with AI insights
- 🎵 **Spotify Integration** - Context-aware music and mood-based playlists

### Advanced Features
- 🧠 **Persistent Memory** - Multi-type memory system (short-term, working, long-term, semantic)
- ⚡ **Background Processing** - Async task execution with RQ/Redis
- � **Workflow Orchestration** - Complete Memory-Chain-Planner workflows
- 🤖 **AI Agent Integration** - Unified MCP system with 15+ productivity tools
- �📱 **Cross-Platform** - Web, mobile, and API interfaces
- 🔒 **User Management** - Context-aware authentication and profiles
- 📈 **Streak Tracking** - AI-powered consistency monitoring
- 🎯 **Goal Setting** - Intelligent weekly and monthly objectives
- 🏆 **Achievements** - Dynamic badges and milestone tracking
- 🔔 **Smart Notifications** - Context-aware reminders and alerts

## Quick Start 🚀

### Prerequisites
- Python 3.8+
- MongoDB running locally  
- Redis (optional, for background tasks)
- OpenAI API key

### Fast Setup
```powershell
# Clone and setup
git clone https://github.com/douglas-danso/focusforge.git
cd focusforge

# Set environment variables
$env:MONGODB_URI = "mongodb://localhost:27017"
$env:OPENAI_API_KEY = "your_openai_api_key_here"
$env:REDIS_URL = "redis://localhost:6379"  # Optional

# Install and start backend
cd backend
pip install -r requirements.txt
python main.py

# Access the Memory-Chain-Planner API
# http://localhost:8000/docs
```

**📖 Detailed Setup**: See [QUICK_START.md](QUICK_START.md) for complete instructions.
**🏗️ Architecture Guide**: See [MEMORY_CHAIN_PLANNER_ARCHITECTURE.md](MEMORY_CHAIN_PLANNER_ARCHITECTURE.md) for detailed architecture documentation.

### Development Options

#### Option 1: Individual Services (Recommended for Development)

```powershell
# Windows PowerShell
.\start-backend.ps1     # Backend + Database + Cache
.\start-frontend.ps1    # Web Application
.\start-mobile.ps1      # Mobile Development Environment
```

```bash
# Linux/Mac
./start-backend.sh      # Backend + Database + Cache  
./start-frontend.sh     # Web Application
./start-mobile.sh       # Mobile Development Environment
```

### Option 2: Service-Specific Docker Compose

```bash
# Backend development (API + DB + Cache)
docker-compose -f docker-compose.backend.yml up -d

# Frontend development (Web app only)
docker-compose -f docker-compose.frontend.yml up -d

# Mobile development (Flutter environment)
docker-compose -f docker-compose.mobile.yml up -d
```

### Option 3: Full Production Stack

```bash
# Complete stack with API Gateway and load balancing
docker-compose -f docker-compose.prod.yml up -d
```

## 📋 Service Access

Once running, access your services:

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | FastAPI backend service |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Web App** | http://localhost:3000 | React web application |
| **Mobile Web** | http://localhost:3001 | Flutter web development |
| **Production** | http://localhost | Full stack via API Gateway |

## ⚙️ Configuration

Create environment files from templates:

```bash
# Backend configuration
cp .env.backend.template .env

# Frontend configuration  
cp .env.frontend.template frontend/.env

# Mobile configuration
cp .env.mobile.template mobile/.env
```

**Required Environment Variables:**
- `OPENAI_API_KEY` - For AI task decomposition
- `SPOTIPY_CLIENT_ID` & `SPOTIPY_CLIENT_SECRET` - For Spotify integration (optional)

## Development Setup 🛠️

### Backend Development

```bash
cd backend
# Install Hatch if you haven't already
pip install hatch

# Create environment and install dependencies
hatch env create

# Start development server
hatch run dev

# Run tests
hatch run test

# Format and lint code
hatch run format
hatch run lint
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Mobile Development

```bash
cd mobile
flutter pub get
flutter run
```

### CLI Development (Legacy)

```bash
pip install -e .  # Install in development mode
focusforge --help
```

## API Endpoints 🔌

### Memory-Chain-Planner Orchestrator
- `POST /api/v1/orchestrator/tasks/create-enhanced` - Complete task creation workflow
- `POST /api/v1/orchestrator/tasks/complete-enhanced` - Complete task completion workflow  
- `POST /api/v1/orchestrator/daily-optimization` - Daily optimization workflow
- `POST /api/v1/orchestrator/focus-session` - Enhanced focus session with AI rituals

### Planner Management
- `GET /api/v1/orchestrator/planner/actions/{user_id}` - Get user's planned actions
- `POST /api/v1/orchestrator/planner/execute/{user_id}` - Execute ready actions
- `DELETE /api/v1/orchestrator/planner/actions/{action_id}` - Cancel action

### Chain Execution
- `POST /api/v1/orchestrator/chains/execute/{chain_name}` - Execute specific chain
- `POST /api/v1/orchestrator/chains/sequence` - Execute chain sequence
- `DELETE /api/v1/orchestrator/chains/cache` - Clear chain cache

### Memory Management
- `GET /api/v1/orchestrator/memory/user-context/{user_id}` - Get user context
- `POST /api/v1/orchestrator/memory/user-context/{user_id}` - Update user context
- `GET /api/v1/orchestrator/memory/similar-tasks/{user_id}` - Search similar tasks

### Background Tasks
- `GET /api/v1/orchestrator/background-tasks/status/{job_id}` - Get task status
- `DELETE /api/v1/orchestrator/background-tasks/{job_id}` - Cancel background task

### Legacy API Endpoints

### Tasks
- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

### Pomodoro
- `POST /api/v1/pomodoro/start` - Start session
- `PUT /api/v1/pomodoro/{id}/complete` - Complete session
- `GET /api/v1/pomodoro` - List sessions

### Analytics
- `GET /api/v1/analytics` - Get user analytics
- `GET /api/v1/analytics/streak` - Current streak
- `GET /api/v1/analytics/weekly` - Weekly stats
- `GET /api/v1/analytics/monthly` - Monthly stats

### Store & Rewards
- `GET /api/v1/store/items` - List store items
- `GET /api/v1/store/profile` - User profile & currency
- `POST /api/v1/store/purchase/{item}` - Purchase item
- `POST /api/v1/store/add-currency/{amount}` - Add currency

### Mood Tracking
- `POST /api/v1/mood` - Log mood
- `GET /api/v1/mood` - Get mood history
- `GET /api/v1/mood/trends` - Mood trends

### Spotify Integration
- `POST /api/v1/spotify/play/{uri}` - Play playlist
- `POST /api/v1/spotify/pause` - Pause playback
- `POST /api/v1/spotify/search` - Search playlists
- `POST /api/v1/spotify/play-by-mood/{mood}` - Mood-based music

## Configuration ⚙️

### Required Environment Variables

```env
# OpenAI (for AI chains and task decomposition)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Memory-Chain-Planner Configuration
REDIS_URL=redis://localhost:6379  # Optional, for background tasks
ENABLE_BACKGROUND_TASKS=true      # Optional, enables RQ processing
MEMORY_CLEANUP_INTERVAL=3600      # Memory cleanup interval (seconds)
CHAIN_EXECUTION_TIMEOUT=60        # Chain execution timeout (seconds)

# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=focusforge

# Spotify (for music integration - optional)
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:3000/callback
```

### Spotify Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/)
2. Create a new app
3. Add redirect URI: `http://localhost:3000/callback`
4. Copy Client ID and Client Secret to `.env`

### OpenAI Setup

1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to `.env` file
3. Ensure you have sufficient credits for API calls

## Project Structure 📁

```
focusforge/
├── backend/                    # FastAPI backend with Memory-Chain-Planner
│   ├── app/
│   │   ├── api/v1/            # API routes (enhanced + legacy)
│   │   │   └── endpoints/     # Orchestrator and legacy endpoints
│   │   ├── core/              # Memory-Chain-Planner implementation
│   │   │   ├── memory.py      # Multi-type memory system
│   │   │   ├── chains.py      # Specialized LangChain workflows
│   │   │   ├── planner.py     # Intelligent action planning
│   │   │   ├── orchestrator.py # Central workflow coordinator
│   │   │   ├── background_tasks.py # RQ/Redis task system
│   │   │   ├── mcp_adapter.py # Unified MCP system (existing)
│   │   │   └── config.py      # Configuration
│   │   ├── models/            # Pydantic schemas
│   │   └── services/          # Business logic services
│   ├── main.py                # FastAPI app with orchestrator
│   └── requirements.txt       # Enhanced dependencies
├── frontend/                  # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/        # Reusable components  
│   │   ├── pages/             # Page components
│   │   └── services/          # API client (enhanced)
│   └── package.json
├── mobile/                    # Flutter mobile app
│   ├── lib/
│   │   ├── core/              # App configuration
│   │   ├── features/          # Feature modules
│   │   └── main.dart
│   └── pubspec.yaml
├── MEMORY_CHAIN_PLANNER_ARCHITECTURE.md  # Architecture documentation
├── QUICK_START.md             # Quick start guide
├── docker-compose.yml         # Multi-service setup
└── README.md
```

## Testing 🧪

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Mobile Tests
```bash
cd mobile
flutter test
```

## Deployment 🚀

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. **Backend**: Deploy FastAPI app to your preferred platform (Heroku, Railway, etc.)
2. **Frontend**: Build and deploy to Vercel, Netlify, or similar
3. **Database**: Use MongoDB Atlas or self-hosted MongoDB
4. **Mobile**: Build and deploy to App Store/Play Store

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Migration from CLI 🔄

If you were using the CLI version:

1. **Export your data**: `focusforge export-data`
2. **Set up the new stack**: Follow the Quick Start guide
3. **Import your data**: Use the import feature in the web interface
4. **Continue using CLI**: The CLI still works alongside the new interfaces

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

- 📧 Email: support@focusforge.app
- 🐛 Issues: [GitHub Issues](https://github.com/douglas-danso/focusforge/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/douglas-danso/focusforge/discussions)

## Roadmap 🗺️

### Completed ✅
- [x] Memory-Chain-Planner architecture implementation
- [x] Multi-type memory system with LangChain compatibility
- [x] Specialized AI chains for task processing
- [x] Intelligent action planning and coordination
- [x] Background task processing with RQ/Redis
- [x] Unified MCP system with 15+ productivity tools
- [x] Enhanced API endpoints for orchestrator workflows
- [x] Complete architecture documentation

### In Progress 🚧
- [ ] Vector store integration (FAISS/Milvus) for semantic search
- [ ] Advanced AI agent implementations
- [ ] Real-time notifications and WebSocket support
- [ ] Complete Google Calendar integration

### Planned 📋
- [ ] Team and workspace management
- [ ] Advanced analytics with pattern recognition
- [ ] Voice commands and control
- [ ] Integration with more productivity tools (Notion, Slack, etc.)
- [ ] AI-powered productivity recommendations
- [ ] Advanced customization and personalization
- [ ] Mobile push notifications
- [ ] Offline mode support

---

Made with ❤️ by [Douglas Danso](https://github.com/douglas-danso)