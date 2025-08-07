# FocusForge MCP Setup and Test Script
# PowerShell script to start MCP server and run tests

param(
    [string]$Action = "test",  # Options: start, test, both
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

# Configuration
$ProjectRoot = $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$MCPServerScript = Join-Path $ProjectRoot "start_mcp_server.py"
$MCPTestScript = Join-Path $ProjectRoot "test_mcp_client.py"

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# Check if Python is available
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Python found: $pythonVersion" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Python not found in PATH" "ERROR"
        return $false
    }
}

# Install required packages
function Install-Requirements {
    Write-Log "Installing Python requirements..."
    
    $requirements = @(
        "fastapi",
        "uvicorn",
        "asyncio",
        "pydantic",
        "python-dotenv"
    )
    
    foreach ($package in $requirements) {
        try {
            Write-Log "Installing $package..."
            pip install $package --quiet
        }
        catch {
            Write-Log "Failed to install $package" "WARN"
        }
    }
    
    Write-Log "Requirements installation completed" "SUCCESS"
}

# Start MCP Server
function Start-MCPServer {
    Write-Log "Starting MCP Server..."
    
    if (-not (Test-Path $MCPServerScript)) {
        Write-Log "MCP server script not found: $MCPServerScript" "ERROR"
        return $false
    }
    
    try {
        # Start server in background
        $job = Start-Job -ScriptBlock {
            param($script)
            python $script
        } -ArgumentList $MCPServerScript
        
        Write-Log "MCP Server started (Job ID: $($job.Id))" "SUCCESS"
        
        # Wait a bit for server to start
        Start-Sleep -Seconds 3
        
        return $job
    }
    catch {
        Write-Log "Failed to start MCP server: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

# Test MCP Implementation
function Test-MCPImplementation {
    Write-Log "Testing MCP implementation..."
    
    if (-not (Test-Path $MCPTestScript)) {
        Write-Log "MCP test script not found: $MCPTestScript" "ERROR"
        return $false
    }
    
    try {
        Write-Log "Running MCP client tests..."
        $result = python $MCPTestScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "MCP tests completed successfully" "SUCCESS"
            return $true
        }
        else {
            Write-Log "MCP tests failed with exit code $LASTEXITCODE" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error running MCP tests: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Stop background jobs
function Stop-BackgroundJobs {
    Write-Log "Stopping background jobs..."
    Get-Job | Stop-Job -PassThru | Remove-Job
    Write-Log "Background jobs stopped" "SUCCESS"
}

# Main execution
function Main {
    Write-Log "FocusForge MCP Setup and Test" "SUCCESS"
    Write-Log "Project Root: $ProjectRoot"
    Write-Log "Action: $Action"
    Write-Log "=" * 50
    
    # Check prerequisites
    if (-not (Test-Python)) {
        Write-Log "Python is required but not found" "ERROR"
        exit 1
    }
    
    # Install requirements
    Install-Requirements
    
    # Execute based on action
    switch ($Action.ToLower()) {
        "start" {
            Write-Log "Starting MCP server only..."
            $serverJob = Start-MCPServer
            if ($serverJob) {
                Write-Log "MCP server is running. Press Ctrl+C to stop."
                try {
                    Wait-Job $serverJob
                }
                finally {
                    Stop-BackgroundJobs
                }
            }
        }
        
        "test" {
            Write-Log "Running tests only..."
            $testResult = Test-MCPImplementation
            if (-not $testResult) {
                exit 1
            }
        }
        
        "both" {
            Write-Log "Starting server and running tests..."
            
            # Start server
            $serverJob = Start-MCPServer
            if (-not $serverJob) {
                Write-Log "Failed to start server" "ERROR"
                exit 1
            }
            
            try {
                # Wait for server to be ready
                Start-Sleep -Seconds 5
                
                # Run tests
                $testResult = Test-MCPImplementation
                
                if ($testResult) {
                    Write-Log "All operations completed successfully!" "SUCCESS"
                }
                else {
                    Write-Log "Tests failed" "ERROR"
                    exit 1
                }
            }
            finally {
                Stop-BackgroundJobs
            }
        }
        
        default {
            Write-Log "Invalid action: $Action. Use 'start', 'test', or 'both'" "ERROR"
            exit 1
        }
    }
    
    Write-Log "Script completed successfully" "SUCCESS"
}

# Error handling
try {
    Main
}
catch {
    Write-Log "Script failed: $($_.Exception.Message)" "ERROR"
    Stop-BackgroundJobs
    exit 1
}
finally {
    if ($Verbose) {
        Write-Log "Cleanup completed"
    }
}
