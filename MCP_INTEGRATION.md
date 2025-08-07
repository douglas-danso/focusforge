# FocusForge MCP Integration

## Overview

FocusForge now includes comprehensive Model Context Protocol (MCP) integration, providing standardized access to all AI agents and productivity tools through a unified interface.

## Architecture

### Components

1. **MCP Server** (`backend/app/mcp/server.py`)
   - Provides 15+ standardized tools
   - Covers all 5 AI agents (TaskBreakdown, Motivation, TaskWeighting, ProofVerification, RitualAdvisor)
   - Handles task management, mood tracking, and gamification

2. **MCP Client** (`backend/app/mcp/client.py`)
   - Async session management
   - Tool calling interface
   - Connection pooling and reconnection

3. **Enhanced LLM Service** (`backend/app/services/llm_service.py`)
   - MCP-enhanced methods with fallback
   - Toggle-able MCP integration
   - Maintains backward compatibility

4. **Configuration** (`backend/app/mcp/config.py`)
   - Centralized MCP settings
   - Tool category organization
   - Environment variable support

## Available Tools

### AI Agents
- `task_breakdown` - Decompose tasks into manageable steps
- `motivation_coach` - Provide personalized motivation
- `task_analysis` - Analyze task complexity and requirements
- `proof_validation` - Validate task completion proof
- `ritual_suggestion` - Suggest productivity rituals
- `comprehensive_guidance` - Combined AI guidance

### Task Management
- `create_task` - Create new tasks
- `update_task` - Update existing tasks
- `get_task` - Retrieve task details
- `list_tasks` - List user tasks

### Mood Tracking
- `log_mood` - Record mood entries
- `get_mood_history` - Retrieve mood trends
- `mood_insights` - Get mood analytics

### Gamification
- `award_points` - Award user points
- `get_user_stats` - Get user statistics
- `unlock_achievement` - Unlock achievements

### Integrations
- `spotify_control` - Control Spotify playback

## Setup and Usage

### 1. Start MCP Server

Using PowerShell (Windows):
```powershell
.\setup_mcp.ps1 -Action start
```

Using Python directly:
```bash
python start_mcp_server.py
```

### 2. Test Implementation

Run all tests:
```powershell
.\setup_mcp.ps1 -Action both
```

Run tests only:
```powershell
.\setup_mcp.ps1 -Action test
```

### 3. API Endpoints

#### MCP Status
```http
GET /api/v1/mcp/status
```

#### List Tools
```http
GET /api/v1/mcp/tools
```

#### Call Tool Directly
```http
POST /api/v1/mcp/tools/{tool_name}/call
```

#### AI Agent Endpoints (MCP Enhanced)
```http
POST /api/v1/mcp/agents/task-breakdown-mcp
POST /api/v1/mcp/agents/motivation-mcp
POST /api/v1/mcp/agents/task-analysis-mcp
POST /api/v1/mcp/agents/proof-validation-mcp
POST /api/v1/mcp/agents/ritual-suggestion-mcp
POST /api/v1/mcp/agents/comprehensive-guidance-mcp
```

### 4. Configuration

Environment variables:
```env
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=3001
MCP_ENABLED=true
```

## Code Examples

### Using MCP Client Directly

```python
from app.mcp.client import MCPSession

async def get_task_breakdown_example():
    async with MCPSession() as mcp:
        result = await mcp.get_task_breakdown(
            title="Write documentation",
            description="Create comprehensive docs",
            duration_minutes=120
        )
        return result
```

### Using Enhanced LLM Service

```python
from app.services.llm_service import LLMService

async def enhanced_task_analysis():
    llm_service = LLMService()
    
    # Will try MCP first, fallback to direct LLM
    result = await llm_service.decompose_task_mcp(
        title="Build API endpoint",
        description="Create REST API for user management",
        duration_minutes=180
    )
    return result
```

### Toggle MCP Integration

```python
# Enable/disable MCP
llm_service.toggle_mcp(True)  # Enable
llm_service.toggle_mcp(False) # Disable and use fallback

# Check MCP status
status = await llm_service.get_mcp_status()
```

## Benefits

1. **Standardization** - Uniform tool interface across all AI agents
2. **Scalability** - Easy to add new tools and capabilities
3. **Reliability** - Fallback mechanisms ensure system stability
4. **Flexibility** - Can toggle MCP on/off without breaking functionality
5. **Context Management** - Better context sharing between tools
6. **Debugging** - Centralized logging and error handling

## Tool Categories

### ai_agents
Core AI functionality for task management and user support

### task_management
CRUD operations for tasks and productivity tracking

### mood_tracking
Emotional state monitoring and analytics

### gamification
Points, achievements, and user engagement

### integrations
External service connections (Spotify, etc.)

## Error Handling

- Graceful degradation when MCP server unavailable
- Automatic fallback to direct LLM calls
- Comprehensive logging for debugging
- Connection retry mechanisms

## Future Extensions

- Additional AI agents and tools
- Real-time notifications via MCP
- Multi-user session management
- Advanced context sharing
- Plugin architecture for custom tools

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check MCP server is running
   - Verify host/port configuration
   - Check firewall settings

2. **Tool Not Found**
   - Verify tool registration in server
   - Check tool name spelling
   - Ensure server has latest tools

3. **Import Errors**
   - Install required dependencies
   - Check Python path configuration
   - Verify backend directory structure

### Logs

- MCP Server: `mcp_server.log`
- Client errors: Check console output
- API errors: FastAPI logs

## Performance

- Async operations throughout
- Connection pooling for efficiency
- Minimal overhead with fallback system
- Tool-level caching where appropriate
