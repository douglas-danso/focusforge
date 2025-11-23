# FocusForge Backend API

The backend API for FocusForge productivity platform, built with FastAPI and Python.

## Features

- **Task Management**: Create, update, and manage productivity tasks
- **AI Task Decomposition**: Break down complex tasks using OpenAI GPT
- **Pomodoro Sessions**: Track focus sessions with timer functionality
- **Mood Tracking**: Log and analyze emotional patterns
- **Analytics**: Comprehensive productivity insights and statistics
- **Reward System**: Gamified points and achievement system
- **Spotify Integration**: Music control and mood-based playlists
- **User Management**: Authentication and user profiles

## Development Setup

### Prerequisites

- Python 3.11+
- Hatch (Python project manager)
- MongoDB
- Redis (optional)

### Using Hatch (Recommended)

1. **Install Hatch**
   ```bash
   pip install hatch
   ```

2. **Clone and setup**
   ```bash
   cd backend
   hatch env create  # Creates virtual environment and installs dependencies
   ```

3. **Run the development server**
   ```bash
   hatch run dev
   # or
   hatch run start
   ```

4. **Run tests**
   ```bash
   hatch run test
   # With coverage
   hatch run test-cov
   ```

5. **Code formatting and linting**
   ```bash
   hatch run format  # Format code with black and isort
   hatch run lint    # Check code style
   hatch run type-check  # Run mypy type checking
   ```

### Using pip (Alternative)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
uvicorn main:app --reload
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=focusforge

# API Keys  
OPENAI_API_KEY=your_openai_api_key
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret

# Security
SECRET_KEY=your_secret_key_here

# Optional
REDIS_URL=redis://localhost:6379
TEMPERATURE=0.3
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## Project Structure

```
backend/
├── app/
│   ├── api/v1/           # API routes and endpoints
│   ├── core/             # Configuration and database setup
│   ├── models/           # Pydantic schemas and data models
│   └── services/         # Business logic and external integrations
├── tests/                # Test files
├── main.py               # FastAPI application entry point
├── pyproject.toml        # Project configuration and dependencies
└── Dockerfile            # Container configuration
```

## Available Commands

```bash
# Development
hatch run dev              # Start development server
hatch run start            # Start production server

# Testing
hatch run test             # Run tests
hatch run test-cov         # Run tests with coverage

# Code Quality
hatch run format           # Format code (black + isort)
hatch run lint             # Lint code (flake8 + black + isort)
hatch run type-check       # Type checking with mypy

# Environment Management
hatch env show             # Show environment info
hatch env remove           # Remove environment
hatch env create           # Create/recreate environment
```

## Deployment

### Docker

```bash
docker build -t focusforge-backend .
docker run -p 8000:8000 --env-file .env focusforge-backend
```

### Production

```bash
hatch build  # Build distribution packages
# Deploy wheel to your preferred platform
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `hatch run test`
5. Format code: `hatch run format`
6. Submit a pull request

## Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework for APIs
- **Uvicorn**: ASGI server for FastAPI
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation and serialization
- **OpenAI**: AI integration for task decomposition
- **Spotipy**: Spotify API integration

### Development Dependencies
- **Pytest**: Testing framework
- **Black**: Code formatter
- **isort**: Import sorter
- **Flake8**: Code linter
- **MyPy**: Static type checker

## License

MIT License - see LICENSE file for details.
