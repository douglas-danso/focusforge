# FocusForge Service Manager (PowerShell)
# This script helps you manage the decoupled FocusForge services

param(
    [Parameter(Position=0)]
    [ValidateSet("status", "start", "stop", "restart", "logs", "help")]
    [string]$Action = "help",
    
    [Parameter(Position=1)]
    [ValidateSet("backend", "frontend", "mobile", "all", "prod")]
    [string]$Service = "all",
    
    [switch]$Follow,
    [switch]$Force
)

function Show-Help {
    Write-Host ""
    Write-Host "🔧 FocusForge Service Manager" -ForegroundColor Cyan
    Write-Host "Manage your decoupled FocusForge services" -ForegroundColor White
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\manage-services.ps1 <action> <service> [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "ACTIONS:" -ForegroundColor Yellow
    Write-Host "  status    Show service status" -ForegroundColor White
    Write-Host "  start     Start services" -ForegroundColor White
    Write-Host "  stop      Stop services" -ForegroundColor White
    Write-Host "  restart   Restart services" -ForegroundColor White
    Write-Host "  logs      View service logs" -ForegroundColor White
    Write-Host "  help      Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "SERVICES:" -ForegroundColor Yellow
    Write-Host "  backend   Backend API + Database + Cache (Port 8000)" -ForegroundColor White
    Write-Host "  frontend  React Web Application (Port 3000)" -ForegroundColor White
    Write-Host "  mobile    Flutter Development Environment (Port 3001)" -ForegroundColor White
    Write-Host "  prod      Full Production Stack with API Gateway (Port 80)" -ForegroundColor White
    Write-Host "  all       All development services (backend + frontend + mobile)" -ForegroundColor White
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "  -Follow   Follow logs in real-time (for logs action)" -ForegroundColor White
    Write-Host "  -Force    Skip confirmations" -ForegroundColor White
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\manage-services.ps1 start backend" -ForegroundColor Cyan
    Write-Host "  .\manage-services.ps1 status all" -ForegroundColor Cyan
    Write-Host "  .\manage-services.ps1 logs frontend -Follow" -ForegroundColor Cyan
    Write-Host "  .\manage-services.ps1 stop all" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🏗️ DECOUPLED ARCHITECTURE BENEFITS:" -ForegroundColor Green
    Write-Host "  ✅ Independent development and deployment" -ForegroundColor White
    Write-Host "  ✅ Scale services individually based on load" -ForegroundColor White
    Write-Host "  ✅ Use different technologies for different services" -ForegroundColor White
    Write-Host "  ✅ Fault isolation - if one service fails, others continue" -ForegroundColor White
    Write-Host "  ✅ Team autonomy - different teams can own different services" -ForegroundColor White
    Write-Host ""
}

function Get-ServiceFiles {
    param([string]$ServiceName)
    
    switch ($ServiceName) {
        "backend" { return "docker-compose.backend.yml" }
        "frontend" { return "docker-compose.frontend.yml" }
        "mobile" { return "docker-compose.mobile.yml" }
        "prod" { return "docker-compose.prod.yml" }
        default { return @("docker-compose.backend.yml", "docker-compose.frontend.yml", "docker-compose.mobile.yml") }
    }
}

function Show-ServiceStatus {
    param([string]$ServiceName)
    
    Write-Host "🔍 Checking service status..." -ForegroundColor Blue
    
    if ($ServiceName -eq "all") {
        $services = @("backend", "frontend", "mobile")
        foreach ($svc in $services) {
            Check-SingleService $svc
        }
    } elseif ($ServiceName -eq "prod") {
        Check-ProductionServices
    } else {
        Check-SingleService $ServiceName
    }
}

function Check-SingleService {
    param([string]$ServiceName)
    
    $port = switch ($ServiceName) {
        "backend" { 8000 }
        "frontend" { 3000 }
        "mobile" { 3001 }
    }
    
    $url = "http://localhost:$port"
    if ($ServiceName -eq "backend") {
        $url += "/health"
    }
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 3 -ErrorAction Stop
        Write-Host "✅ $ServiceName is running on port $port" -ForegroundColor Green
    } catch {
        Write-Host "❌ $ServiceName is not responding on port $port" -ForegroundColor Red
    }
}

function Check-ProductionServices {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/health" -TimeoutSec 3 -ErrorAction Stop
        Write-Host "✅ Production stack is running on port 80" -ForegroundColor Green
    } catch {
        Write-Host "❌ Production stack is not responding on port 80" -ForegroundColor Red
    }
}

function Start-Services {
    param([string]$ServiceName)
    
    Write-Host "🚀 Starting $ServiceName services..." -ForegroundColor Green
    
    $files = Get-ServiceFiles $ServiceName
    
    if ($ServiceName -eq "all") {
        foreach ($file in $files) {
            Write-Host "Starting services from $file..." -ForegroundColor Yellow
            docker-compose -f $file up -d
            if ($LASTEXITCODE -ne 0) {
                Write-Host "❌ Failed to start services from $file" -ForegroundColor Red
                return
            }
        }
    } else {
        docker-compose -f $files up -d
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to start $ServiceName services" -ForegroundColor Red
            return
        }
    }
    
    Write-Host "✅ Services started successfully!" -ForegroundColor Green
    Start-Sleep -Seconds 3
    Show-ServiceStatus $ServiceName
}

function Stop-Services {
    param([string]$ServiceName)
    
    if (-not $Force) {
        $confirmation = Read-Host "Are you sure you want to stop $ServiceName services? (y/N)"
        if ($confirmation -ne "y" -and $confirmation -ne "Y") {
            Write-Host "Operation cancelled." -ForegroundColor Yellow
            return
        }
    }
    
    Write-Host "🛑 Stopping $ServiceName services..." -ForegroundColor Yellow
    
    $files = Get-ServiceFiles $ServiceName
    
    if ($ServiceName -eq "all") {
        foreach ($file in $files) {
            Write-Host "Stopping services from $file..." -ForegroundColor Yellow
            docker-compose -f $file down
        }
    } else {
        docker-compose -f $files down
    }
    
    Write-Host "✅ Services stopped successfully!" -ForegroundColor Green
}

function Restart-Services {
    param([string]$ServiceName)
    
    Write-Host "🔄 Restarting $ServiceName services..." -ForegroundColor Blue
    Stop-Services $ServiceName
    Start-Sleep -Seconds 2
    Start-Services $ServiceName
}

function Show-Logs {
    param([string]$ServiceName)
    
    $files = Get-ServiceFiles $ServiceName
    $followFlag = if ($Follow) { "-f" } else { "" }
    
    Write-Host "📋 Showing logs for $ServiceName services..." -ForegroundColor Blue
    
    if ($ServiceName -eq "all") {
        Write-Host "Use Ctrl+C to stop following logs" -ForegroundColor Yellow
        foreach ($file in $files) {
            Write-Host "=== Logs from $file ===" -ForegroundColor Cyan
            docker-compose -f $file logs $followFlag
        }
    } else {
        if ($Follow) {
            Write-Host "Use Ctrl+C to stop following logs" -ForegroundColor Yellow
        }
        docker-compose -f $files logs $followFlag
    }
}

# Main execution
switch ($Action) {
    "status" { Show-ServiceStatus $Service }
    "start" { Start-Services $Service }
    "stop" { Stop-Services $Service }
    "restart" { Restart-Services $Service }
    "logs" { Show-Logs $Service }
    "help" { Show-Help }
    default { Show-Help }
}
