# FocusForge MCP Endpoint Tests (PowerShell)
# Run this script to test the MCP integration

Write-Host "🚀 Testing FocusForge MCP Integration" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

$baseUrl = "http://localhost:8000"

# Test 1: Health check
Write-Host ""
Write-Host "1️⃣ Testing health endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: MCP Status
Write-Host ""
Write-Host "2️⃣ Testing MCP status..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/mcp/status" -Method Get
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: List MCP Tools
Write-Host ""
Write-Host "3️⃣ Testing MCP tools list..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/mcp/tools" -Method Get
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: MCP Health Check
Write-Host ""
Write-Host "4️⃣ Testing MCP health..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/mcp/health" -Method Get
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Task Breakdown via MCP
Write-Host ""
Write-Host "5️⃣ Testing MCP task breakdown..." -ForegroundColor Cyan
try {
    $taskData = @{
        task_data = @{
            title = "Write API documentation"
            description = "Create comprehensive documentation for all endpoints"
            duration_minutes = 90
        }
    }
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/mcp/agents/task-breakdown-mcp" -Method Post -Body ($taskData | ConvertTo-Json -Depth 10) -ContentType "application/json"
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Motivation via MCP
Write-Host ""
Write-Host "6️⃣ Testing MCP motivation..." -ForegroundColor Cyan
try {
    $motivationData = @{
        user_id = "test_user"
        current_mood = "tired"
        challenge = "feeling overwhelmed with tasks"
    }
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/mcp/agents/motivation-mcp" -Method Post -Body ($motivationData | ConvertTo-Json) -ContentType "application/json"
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Toggle MCP
Write-Host ""
Write-Host "7️⃣ Testing MCP toggle..." -ForegroundColor Cyan
try {
    $toggleData = @{
        enabled = $true
    }
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/mcp/toggle" -Method Post -Body ($toggleData | ConvertTo-Json) -ContentType "application/json"
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "✨ MCP endpoint testing completed!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
