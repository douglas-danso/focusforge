# FocusForge Frontend Service Startup Script (PowerShell)

param(
    [switch]$SkipHealthCheck,
    [switch]$Force
)

Write-Host "🌐 Starting FocusForge Frontend Service..." -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Create frontend-specific .env file if it doesn't exist
if (-not (Test-Path "frontend\.env")) {
    Write-Host "📝 Creating frontend .env file..." -ForegroundColor Yellow
    $envContent = @"
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
REACT_APP_ENV=development
GENERATE_SOURCEMAP=true
CHOKIDAR_USEPOLLING=true
"@
    $envContent | Out-File -FilePath "frontend\.env" -Encoding UTF8
}

Write-Host "📋 Frontend Service Configuration:" -ForegroundColor Cyan
Write-Host "   - Frontend Port: 3000" -ForegroundColor White
Write-Host "   - API Backend: http://localhost:8000/api/v1" -ForegroundColor White
Write-Host "   - WebSocket: ws://localhost:8000/ws" -ForegroundColor White

# Check if backend is running (optional)
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Backend service detected on port 8000" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend service not detected. Frontend will still start but API calls may fail." -ForegroundColor Yellow
    Write-Host "   To start backend: .\start-backend.ps1" -ForegroundColor Cyan
}

# Start frontend service
Write-Host "🔧 Starting frontend service..." -ForegroundColor Blue
docker-compose -f docker-compose.frontend.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start frontend service" -ForegroundColor Red
    exit 1
}

# Wait for service to be ready
Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

if (-not $SkipHealthCheck) {
    # Health check
    Write-Host "🔍 Checking frontend health..." -ForegroundColor Blue
    
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Frontend is running on http://localhost:3000" -ForegroundColor Green
                break
            }
        } catch {
            if ($attempt -eq $maxAttempts) {
                Write-Host "❌ Frontend failed to start after $maxAttempts attempts" -ForegroundColor Red
                Write-Host "📋 Checking logs..." -ForegroundColor Yellow
                docker-compose -f docker-compose.frontend.yml logs frontend
                exit 1
            }
            Write-Host "⏳ Attempt $attempt/$maxAttempts - waiting for frontend..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
            $attempt++
        }
    }
}

Write-Host ""
Write-Host "🎉 Frontend Service is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Web Application: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Management Commands:" -ForegroundColor Cyan
Write-Host "   View logs: docker-compose -f docker-compose.frontend.yml logs -f" -ForegroundColor White
Write-Host "   Stop service: docker-compose -f docker-compose.frontend.yml down" -ForegroundColor White
Write-Host "   Restart service: docker-compose -f docker-compose.frontend.yml restart" -ForegroundColor White
Write-Host "   Shell access: docker exec -it focusforge-frontend sh" -ForegroundColor White
Write-Host ""
Write-Host "💡 Development Tips:" -ForegroundColor Yellow
Write-Host "   - Hot reload is enabled - changes will reflect immediately" -ForegroundColor White
Write-Host "   - Check browser console for any API connection issues" -ForegroundColor White
Write-Host "   - Ensure backend service is running for full functionality" -ForegroundColor White
Write-Host ""
Write-Host "Happy focusing! 🚀" -ForegroundColor Green
