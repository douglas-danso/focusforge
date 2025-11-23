from fastapi import APIRouter
from app.api.v1.endpoints import tasks, users, pomodoro, mood, analytics, spotify, store, calendar, auth

# Import new endpoints
try:
    from app.api.v1.endpoints import rituals
    rituals_available = True
except ImportError:
    rituals_available = False

try:
    from app.api.v1.endpoints import proofs
    proofs_available = True
except ImportError:
    proofs_available = False

# Import MCP router if available
try:
    from app.api.v1.endpoints import mcp
    mcp_available = True
except ImportError:
    mcp_available = False

# Import orchestrator router
try:
    from app.api.v1.endpoints import orchestrator
    orchestrator_available = True
except ImportError:
    orchestrator_available = False

api_router = APIRouter()

# Authentication routes (no auth required)
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
# Removed agents.router - functionality is now handled by orchestrator
api_router.include_router(pomodoro.router, prefix="/pomodoro", tags=["pomodoro"])
api_router.include_router(mood.router, prefix="/mood", tags=["mood"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(spotify.router, prefix="/spotify", tags=["spotify"])
api_router.include_router(store.router, prefix="/store", tags=["store"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])

# Include new feature routers
if rituals_available:
    api_router.include_router(rituals.router, prefix="/rituals", tags=["rituals"])

if proofs_available:
    api_router.include_router(proofs.router, prefix="/proofs", tags=["proofs"])

# Include MCP router if available (for debugging and direct tool access)
if mcp_available:
    api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp-tools"])

# Include orchestrator router if available (main Memory-Chain-Planner interface)
if orchestrator_available:
    api_router.include_router(orchestrator.router, prefix="/orchestrator", tags=["memory-chain-planner"])
