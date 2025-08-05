@echo off
REM FocusForge Development Setup Script for Windows
echo 🔥 Setting up FocusForge Development Environment...

REM Check if .env exists, create from example if not
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your API keys before continuing!
    echo    - OpenAI API key for task decomposition
    echo    - Spotify credentials for music integration
    pause
)

REM Check if Hatch is installed
echo 🔍 Checking for Hatch installation...
hatch --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing Hatch for Python project management...
    pip install hatch
) else (
    echo ✅ Hatch is already installed
)

REM Start services with Docker Compose
echo 🐳 Starting services with Docker Compose...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check services
echo 🔍 Checking service health...

REM Check backend
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Backend API is running on http://localhost:8000
    echo 📚 API Documentation: http://localhost:8000/docs
) else (
    echo ❌ Backend API is not responding
)

REM Check frontend
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Frontend is running on http://localhost:3000
) else (
    echo ❌ Frontend is not responding
)

echo.
echo 🎉 FocusForge is ready!
echo.
echo 🌐 Web App: http://localhost:3000
echo 🔗 API: http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo.
echo 💡 Development Tips:
echo    - Backend (Hatch): cd backend && hatch run dev
echo    - Frontend (npm): cd frontend && npm start
echo    - View logs: docker-compose logs -f
echo    - Stop services: docker-compose down
echo.
echo Happy focusing! 🚀
pause
