from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from app.mcp.client import get_mcp_client, MCPSession
from app.mcp.config import get_mcp_config
from app.services.llm_service import LLMService

router = APIRouter()

@router.get("/status", response_model=Dict[str, Any])
async def get_mcp_status():
    """Get MCP server status and capabilities"""
    try:
        llm_service = LLMService()
        status = await llm_service.get_mcp_status()
        config = get_mcp_config()
        
        return {
            "mcp_server": status,
            "configuration": config["server"],
            "available_categories": list(config["tools"].keys()),
            "total_tools": sum(len(tools) for tools in config["tools"].values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools", response_model=Dict[str, Any])
async def list_mcp_tools():
    """List all available MCP tools"""
    try:
        async with MCPSession() as mcp:
            tools = await mcp.list_tools()
            config = get_mcp_config()
        
            
            # Organize tools by category
            categorized_tools = {}
            for category, tool_names in config["tools"].items():
                categorized_tools[category] = [
                    tool for tool in tools 
                    if tool.get("name") in tool_names
                ]
            
            return {
                "success": True,
                "tools_by_category": categorized_tools,
                "total_tools": len(tools),
                "raw_tools": tools
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/{tool_name}/call", response_model=Dict[str, Any])
async def call_mcp_tool(
    tool_name: str,
    arguments: Dict[str, Any]
):
    """Call a specific MCP tool directly"""
    try:
        async with MCPSession() as mcp:
            result = await mcp.call_tool(tool_name, arguments)
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
                "timestamp": "2025-08-07T00:00:00Z"  # Current timestamp
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== AI AGENT ENDPOINTS VIA MCP =====

@router.post("/agents/task-breakdown-mcp", response_model=Dict[str, Any])
async def task_breakdown_mcp(
    task_data: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
):
    """Get task breakdown via MCP"""
    try:
        async with MCPSession() as mcp:
            result = await mcp.get_task_breakdown(
                title=task_data.get("title", ""),
                description=task_data.get("description", ""),
                duration_minutes=task_data.get("duration_minutes", 25),
                user_context=user_context
            )
            
            return {
                "success": result.get("success", False),
                "breakdown": result.get("breakdown", []),
                "via_mcp": True,
                "tool": "task_breakdown"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/motivation-mcp", response_model=Dict[str, Any])
async def motivation_mcp(
    user_id: str,
    current_mood: str = "neutral",
    challenge: str = "",
    context: Optional[Dict[str, Any]] = None
):
    """Get motivation via MCP"""
    try:
        async with MCPSession() as mcp:
            result = await mcp.get_motivation(
                user_id=user_id,
                current_mood=current_mood,
                challenge=challenge,
                context=context or {}
            )
            
            return {
                "success": result.get("success", False),
                "motivation": result.get("motivation", ""),
                "via_mcp": True,
                "tool": "motivation_coach"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/task-analysis-mcp", response_model=Dict[str, Any])
async def task_analysis_mcp(
    task_data: Dict[str, Any],
    user_skill_level: str = "intermediate"
):
    """Get task analysis via MCP"""
    try:
        async with MCPSession() as mcp:
            result = await mcp.get_task_analysis(
                title=task_data.get("title", ""),
                description=task_data.get("description", ""),
                duration_minutes=task_data.get("duration_minutes", 25),
                user_skill_level=user_skill_level
            )
            
            return {
                "success": result.get("success", False),
                "analysis": result.get("analysis", {}),
                "via_mcp": True,
                "tool": "task_analysis"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/proof-validation-mcp", response_model=Dict[str, Any])
async def proof_validation_mcp(
    validation_data: Dict[str, Any]
):
    """Validate proof via MCP"""
    try:
        async with MCPSession() as mcp:
            result = await mcp.validate_proof(
                task_description=validation_data.get("task_description", ""),
                proof_text=validation_data.get("proof_text", ""),
                completion_criteria=validation_data.get("completion_criteria", "")
            )
            
            return {
                "success": result.get("success", False),
                "validation": result.get("validation", {}),
                "via_mcp": True,
                "tool": "proof_validation"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/ritual-suggestion-mcp", response_model=Dict[str, Any])
async def ritual_suggestion_mcp(
    ritual_request: Dict[str, Any]
):
    """Get ritual suggestion via MCP"""
    try:
        async with MCPSession() as mcp:
            result = await mcp.get_ritual_suggestion(
                user_mood=ritual_request.get("mood", "neutral"),
                task_type=ritual_request.get("task_type", "general"),
                time_of_day=ritual_request.get("time_of_day", "morning"),
                preferences=ritual_request.get("preferences", {})
            )
            
            return {
                "success": result.get("success", False),
                "ritual": result.get("ritual", {}),
                "via_mcp": True,
                "tool": "ritual_suggestion"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/comprehensive-guidance-mcp", response_model=Dict[str, Any])
async def comprehensive_guidance_mcp(
    user_id: str,
    task_data: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
):
    """Get comprehensive guidance via MCP"""
    try:
        async with MCPSession() as mcp:
            result = await mcp.get_comprehensive_guidance(
                user_id=user_id,
                task_data=task_data,
                user_context=user_context
            )
            
            return {
                "success": result.get("success", False),
                "guidance": result.get("guidance", {}),
                "via_mcp": True,
                "tool": "comprehensive_guidance"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== MCP MANAGEMENT ENDPOINTS =====

@router.post("/toggle", response_model=Dict[str, Any])
async def toggle_mcp(
    enabled: bool = True
):
    """Toggle MCP integration on/off"""
    try:
        llm_service = LLMService()
        llm_service.toggle_mcp(enabled)
        
        return {
            "success": True,
            "mcp_enabled": enabled,
            "message": f"MCP integration {'enabled' if enabled else 'disabled'}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=Dict[str, Any])
async def mcp_health_check():
    """Health check for MCP server"""
    try:
        async with MCPSession() as mcp:
            # Try a simple tool call to verify connectivity
            tools = await mcp.list_tools()
            
            return {
                "healthy": True,
                "connected": mcp.connected,
                "tools_available": len(tools),
                "timestamp": "2025-08-07T00:00:00Z"
            }
    except Exception as e:
        return {
            "healthy": False,
            "connected": False,
            "error": str(e),
            "timestamp": "2025-08-07T00:00:00Z"
        }
