param(
    [switch]$SkipHealthCheck,
    [switch]$Force
)

Write-Host "Starting FocusForge Backend Service..." -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
}
catch {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    if (Test-Path ".env.template") {
        Copy-Item ".env.template" ".env"
        Write-Host "WARNING: Please edit .env file with your configuration before proceeding." -ForegroundColor Yellow
        if (-not $Force) {
            Read-Host "Press Enter to continue"
        }
    }
    else {
        Write-Host "ERROR: .env.template file not found. Creating basic template..." -ForegroundColor Red
        $envContent = @"
# Backend Configuration
OPENAI_API_KEY=your-openai-api-key-here
SPOTIPY_CLIENT_ID=your-spotify-client-id
SPOTIPY_CLIENT_SECRET=your-spotify-client-secret
SPOTIPY_REDIRECT_URI=http://localhost:8000/callback
MONGODB_URI=mongodb://localhost:27017/focusforge
DATABASE_NAME=focusforge
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
"@
        Set-Content -Path ".env" -Value $envContent -Encoding UTF8
        Write-Host "WARNING: Please edit .env file with your API keys before proceeding." -ForegroundColor Yellow
        if (-not $Force) {
            Read-Host "Press Enter to continue"
        }
    }
}

Write-Host "Backend Service Configuration:" -ForegroundColor Cyan
Write-Host "   - API Port: 8000" -ForegroundColor White
Write-Host "   - Database: MongoDB (localhost:27017)" -ForegroundColor White
Write-Host "   - Cache: Redis (localhost:6379)" -ForegroundColor White
Write-Host "   - Environment: focusforge" -ForegroundColor White

# Start backend services
Write-Host "Starting backend infrastructure..." -ForegroundColor Blue
docker-compose -f docker-compose.backend.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start backend services" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

if (-not $SkipHealthCheck) {
    # Health check
    Write-Host "Checking service health..." -ForegroundColor Blue
    
    $maxAttempts = 10
    $attempt = 1
    $backendHealthy = $false
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8004/health" -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "SUCCESS: Backend API is running on http://localhost:8004" -ForegroundColor Green
                Write-Host "API Documentation: http://localhost:8004/docs" -ForegroundColor Cyan
                Write-Host "Interactive API: http://localhost:8004/redoc" -ForegroundColor Cyan
                $backendHealthy = $true
                break
            }
        }
        catch {
            if ($attempt -eq $maxAttempts) {
                Write-Host "ERROR: Backend API is not responding after $maxAttempts attempts" -ForegroundColor Red
                Write-Host "Checking logs..." -ForegroundColor Yellow
                docker-compose -f docker-compose.backend.yml logs backend
                exit 1
            }
            Write-Host "Attempt $attempt/$maxAttempts - waiting for backend..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
            $attempt++
        }
    }

    # Check MongoDB
    try {
        docker exec focusforge-mongo mongosh --eval "db.adminCommand('ping')" | Out-Null
        Write-Host "SUCCESS: MongoDB is running on localhost:27017" -ForegroundColor Green
    }
    catch {
        Write-Host "ERROR: MongoDB is not responding" -ForegroundColor Red
    }

    # Check Redis
    try {
        docker exec focusforge-redis redis-cli ping | Out-Null
        Write-Host "SUCCESS: Redis is running on localhost:6379" -ForegroundColor Green
    }
    catch {
        Write-Host "ERROR: Redis is not responding" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Backend Service is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Management Commands:" -ForegroundColor Cyan
Write-Host "   View logs: docker-compose -f docker-compose.backend.yml logs -f" -ForegroundColor White
Write-Host "   Stop service: docker-compose -f docker-compose.backend.yml down" -ForegroundColor White
Write-Host "   Restart service: docker-compose -f docker-compose.backend.yml restart" -ForegroundColor White
Write-Host "   Database shell: docker exec -it focusforge-mongo mongosh focusforge" -ForegroundColor White
Write-Host "   Redis CLI: docker exec -it focusforge-redis redis-cli" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding!" -ForegroundColor Green