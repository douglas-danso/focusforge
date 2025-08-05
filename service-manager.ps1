# FocusForge Simple Service Manager (PowerShell)
param(
    [Parameter(Position=0)]
    [ValidateSet("status", "start", "stop", "restart", "logs", "help")]
    [string]$Action = "help",
    
    [Parameter(Position=1)]
    [ValidateSet("backend", "frontend", "mobile", "all", "prod")]
    [string]$Service = "all",
    
    [switch]$Follow
)

function Show-Help {
    Write-Host ""
    Write-Host "🔧 FocusForge Service Manager" -ForegroundColor Cyan
    Write-Host "Manage your decoupled FocusForge services" -ForegroundColor White
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\service-manager.ps1 <action> <service>" -ForegroundColor White
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
    Write-Host "  prod      Full Production Stack (Port 80)" -ForegroundColor White
    Write-Host "  all       All development services" -ForegroundColor White
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\service-manager.ps1 start backend" -ForegroundColor Cyan
    Write-Host "  .\service-manager.ps1 status all" -ForegroundColor Cyan
    Write-Host "  .\service-manager.ps1 logs frontend -Follow" -ForegroundColor Cyan
    Write-Host ""
}

function Get-ServiceFile {
    param([string]$ServiceName)
    
    switch ($ServiceName) {
        "backend" { return "docker-compose.backend.yml" }
        "frontend" { return "docker-compose.frontend.yml" }
        "mobile" { return "docker-compose.mobile.yml" }
        "prod" { return "docker-compose.prod.yml" }
        default { return "" }
    }
}

function Check-ServiceHealth {
    param([string]$ServiceName, [int]$Port)
    
    $url = "http://localhost:$Port"
    if ($ServiceName -eq "backend") {
        $url += "/health"
    }
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 3 -ErrorAction Stop
        Write-Host "✅ $ServiceName is running on port $Port" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ $ServiceName is not responding on port $Port" -ForegroundColor Red
        return $false
    }
}

function Show-ServiceStatus {
    param([string]$ServiceName)
    
    Write-Host "🔍 Checking service status..." -ForegroundColor Blue
    
    if ($ServiceName -eq "all") {
        Check-ServiceHealth "backend" 8000
        Check-ServiceHealth "frontend" 3000
        Check-ServiceHealth "mobile" 3001
    } elseif ($ServiceName -eq "prod") {
        Check-ServiceHealth "production" 80
    } else {
        $port = switch ($ServiceName) {
            "backend" { 8000 }
            "frontend" { 3000 }
            "mobile" { 3001 }
        }
        Check-ServiceHealth $ServiceName $port
    }
}

function Start-Services {
    param([string]$ServiceName)
    
    Write-Host "🚀 Starting $ServiceName services..." -ForegroundColor Green
    
    if ($ServiceName -eq "all") {
        $services = @("backend", "frontend", "mobile")
        foreach ($svc in $services) {
            $file = Get-ServiceFile $svc
            Write-Host "Starting $svc..." -ForegroundColor Yellow
            docker-compose -f $file up -d
        }
    } else {
        $file = Get-ServiceFile $ServiceName
        if ($file) {
            docker-compose -f $file up -d
        } else {
            Write-Host "❌ Unknown service: $ServiceName" -ForegroundColor Red
            return
        }
    }
    
    Write-Host "✅ Services started!" -ForegroundColor Green
}

function Stop-Services {
    param([string]$ServiceName)
    
    Write-Host "🛑 Stopping $ServiceName services..." -ForegroundColor Yellow
    
    if ($ServiceName -eq "all") {
        $services = @("backend", "frontend", "mobile")
        foreach ($svc in $services) {
            $file = Get-ServiceFile $svc
            docker-compose -f $file down
        }
    } else {
        $file = Get-ServiceFile $ServiceName
        if ($file) {
            docker-compose -f $file down
        }
    }
    
    Write-Host "✅ Services stopped!" -ForegroundColor Green
}

function Show-Logs {
    param([string]$ServiceName)
    
    $file = Get-ServiceFile $ServiceName
    if (-not $file) {
        Write-Host "❌ Unknown service: $ServiceName" -ForegroundColor Red
        return
    }
    
    $followFlag = if ($Follow) { "-f" } else { "" }
    
    Write-Host "📋 Showing logs for $ServiceName..." -ForegroundColor Blue
    if ($Follow) {
        Write-Host "Use Ctrl+C to stop following logs" -ForegroundColor Yellow
    }
    
    docker-compose -f $file logs $followFlag
}

# Main execution
switch ($Action) {
    "status" { Show-ServiceStatus $Service }
    "start" { Start-Services $Service }
    "stop" { Stop-Services $Service }
    "restart" { 
        Stop-Services $Service
        Start-Sleep -Seconds 2
        Start-Services $Service
    }
    "logs" { Show-Logs $Service }
    "help" { Show-Help }
    default { Show-Help }
}
