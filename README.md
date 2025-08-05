# FocusForge 🔥

A comprehensive productivity and focus management platform with AI-powered task decomposition, Pomodoro timer, mood tracking, and gamification elements.

## Architecture

FocusForge follows a **fully decoupled microservices architecture**:

- **🔗 Backend API** (FastAPI + Python) - Core business logic and data processing
- **🌐 Web Frontend** (React + Material-UI) - Responsive web application
- **📱 Mobile App** (Flutter) - Cross-platform mobile application
- **🚪 API Gateway** (NGINX) - Load balancing and routing in production
- **💾 Database** (MongoDB) - Data persistence
- **⚡ Cache** (Redis) - Session storage and caching

Each service can be developed, deployed, and scaled independently.

## Features ✨

### Core Functionality
- 🍅 **Pomodoro Timer** - Customizable focus sessions with break management
- 📝 **Task Management** - Create, organize, and track your tasks
- 🤖 **AI Task Decomposition** - Break down complex tasks using GPT
- 📊 **Analytics & Insights** - Track your productivity patterns
- 🏪 **Reward Store** - Gamified rewards system
- 😊 **Mood Tracking** - Log and analyze your emotional patterns
- 🎵 **Spotify Integration** - Focus music and mood-based playlists

### Advanced Features
- 📱 **Cross-Platform** - Web, mobile, and CLI interfaces
- 🔒 **User Management** - Authentication and user profiles
- 📈 **Streak Tracking** - Daily consistency monitoring
- 🎯 **Goal Setting** - Weekly and monthly objectives
- 🏆 **Achievements** - Unlock badges and milestones
- 🔔 **Notifications** - Session reminders and completion alerts

## Quick Start 🚀

### Option 1: Individual Services (Recommended for Development)

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
# OpenAI (for task decomposition)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Spotify (for music integration)
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:3000/callback

# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=focusforge
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
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Configuration & database
│   │   ├── models/         # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── main.py             # FastAPI app
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   └── services/       # API client
│   └── package.json
├── mobile/                 # Flutter mobile app
│   ├── lib/
│   │   ├── core/           # App configuration
│   │   ├── features/       # Feature modules
│   │   └── main.dart
│   └── pubspec.yaml
├── src/                    # Legacy CLI code
├── docker-compose.yml      # Multi-service setup
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

- [ ] Real-time collaboration features
- [ ] Advanced analytics and insights
- [ ] Integration with more productivity tools
- [ ] Voice commands and control
- [ ] AI-powered productivity recommendations
- [ ] Team and workspace management
- [ ] Advanced customization options

---

Made with ❤️ by [Douglas Danso](https://github.com/douglas-danso)