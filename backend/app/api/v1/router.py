from fastapi import APIRouter
from app.api.v1.endpoints import tasks, users, pomodoro, mood, analytics, spotify, store, agents

# Import MCP router if available
try:
    from app.api.v1.endpoints import mcp
    mcp_available = True
except ImportError:
    mcp_available = False

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(agents.router, prefix="/agents", tags=["ai-agents"])
api_router.include_router(pomodoro.router, prefix="/pomodoro", tags=["pomodoro"])
api_router.include_router(mood.router, prefix="/mood", tags=["mood"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(spotify.router, prefix="/spotify", tags=["spotify"])
api_router.include_router(store.router, prefix="/store", tags=["store"])

# Include MCP router if available
if mcp_available:
    api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
