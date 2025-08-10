from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/tools")
async def list_available_tools() -> Dict[str, Any]:
    """List all available MCP tools"""
    try:
        from app.core.unified_mcp import unified_mcp
        tools = unified_mcp.list_tools()
        
        return {
            "success": True,
            "tools": tools,
            "tool_count": len(tools)
        }
    except Exception as e:
        logger.error(f"Error listing MCP tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/{tool_name}")
async def call_mcp_tool(tool_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call a specific MCP tool"""
    try:
        from app.core.unified_mcp import unified_mcp
        
        result = await unified_mcp.call_tool(tool_name, parameters or {})
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Tool execution failed"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calling MCP tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_mcp_status() -> Dict[str, Any]:
    """Get MCP system status"""
    try:
        from app.core.unified_mcp import unified_mcp
        
        tools = unified_mcp.list_tools()
        
        return {
            "success": True,
            "status": "active",
            "system": "unified_mcp",
            "tool_count": len(tools),
            "categories": list(set(tool.get("category", "unknown") for tool in tools))
        }
    except Exception as e:
        logger.error(f"Error getting MCP status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Convenience endpoints for common AI operations
@router.post("/ai/task-breakdown")
async def ai_task_breakdown(
    title: str,
    description: str = "",
    duration_minutes: int = 60,
    user_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Break down a task using AI"""
    try:
        from app.core.unified_mcp import unified_mcp
        
        result = await unified_mcp.call_tool(
            "ai_task_breakdown",
            {
                "title": title,
                "description": description,
                "duration_minutes": duration_minutes,
                "user_context": user_context or {}
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in AI task breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/motivation")
async def ai_motivation(
    user_context: Dict[str, Any],
    current_mood: str,
    challenge: str = "",
    completed_tasks: List[Dict] = None
) -> Dict[str, Any]:
    """Get AI-powered motivation"""
    try:
        from app.core.unified_mcp import unified_mcp
        
        result = await unified_mcp.call_tool(
            "ai_motivation",
            {
                "user_context": user_context,
                "current_mood": current_mood,
                "challenge": challenge,
                "completed_tasks": completed_tasks or []
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in AI motivation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/ritual-suggestion")
async def ai_ritual_suggestion(
    user_mood: str,
    task_type: str,
    time_of_day: str,
    preferences: Dict[str, Any] = None,
    history: List[Dict] = None
) -> Dict[str, Any]:
    """Get AI ritual suggestions"""
    try:
        from app.core.unified_mcp import unified_mcp
        
        result = await unified_mcp.call_tool(
            "ai_ritual_suggestion",
            {
                "user_mood": user_mood,
                "task_type": task_type,
                "time_of_day": time_of_day,
                "preferences": preferences or {},
                "history": history or []
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in AI ritual suggestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
