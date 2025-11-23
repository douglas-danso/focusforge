from fastapi import APIRouter, HTTPException, Path, Query
from typing import Dict, Any, List
import logging

from app.models.api_schemas import (
    MCPToolsResponse, MCPToolCallRequest, MCPToolCallResponse,
    MCPStatusResponse, AITaskBreakdownRequest, AIMotivationRequest,
    AIRitualRequest, MCPToolInfo, create_error_response
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/tools", response_model=MCPToolsResponse)
async def list_available_tools() -> MCPToolsResponse:
    """List all available MCP tools"""
    try:
        from app.core.unified_mcp import unified_mcp
        tools_by_category = unified_mcp.get_available_tools()
        
        # Flatten the tools list for the response
        all_tools = []
        for category, tools in tools_by_category.items():
            for tool in tools:
                tool_info = MCPToolInfo(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool["parameters"],
                    category=category
                )
                all_tools.append(tool_info)
        
        # Convert tools_by_category to use MCPToolInfo objects
        tools_by_category_typed = {}
        for category, tools in tools_by_category.items():
            tools_by_category_typed[category] = [
                MCPToolInfo(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool["parameters"],
                    category=category
                )
                for tool in tools
            ]
        
        return MCPToolsResponse(
            success=True,
            tools=all_tools,
            tools_by_category=tools_by_category_typed,
            tool_count=len(all_tools)
        )
    except Exception as e:
        logger.error(f"Error listing MCP tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/{tool_name}", response_model=MCPToolCallResponse)
async def call_mcp_tool(
    tool_name: str = Path(..., description="Name of the MCP tool to call"),
    request: MCPToolCallRequest = MCPToolCallRequest()
) -> MCPToolCallResponse:
    """Call a specific MCP tool"""
    try:
        from app.core.unified_mcp import unified_mcp
        
        result = await unified_mcp.call_tool(tool_name, request.parameters)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Tool execution failed"))
        
        return MCPToolCallResponse(
            success=True,
            tool=tool_name,
            result=result.get("result"),
            timestamp=result.get("timestamp")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calling MCP tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=MCPStatusResponse)
async def get_mcp_status() -> MCPStatusResponse:
    """Get MCP system status"""
    try:
        from app.core.unified_mcp import unified_mcp
        
        status = await unified_mcp.get_system_status()
        
        return MCPStatusResponse(
            success=True,
            status="active" if status.get("initialized") else "inactive",
            system="unified_mcp",
            initialized=status.get("initialized", False),
            tools_count=status.get("tools_count", 0),
            services_available=status.get("services_available", []),
            categories=status.get("categories", []),
            tools_by_category=status.get("tools_by_category", {}),
            timestamp=status.get("timestamp")
        )
    except Exception as e:
        logger.error(f"Error getting MCP status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Convenience endpoints for common AI operations
@router.post("/ai/task-breakdown", response_model=MCPToolCallResponse)
async def ai_task_breakdown(request: AITaskBreakdownRequest) -> MCPToolCallResponse:
    """Break down a task using AI"""
    try:
        from app.core.unified_mcp import unified_mcp
        
        result = await unified_mcp.call_tool(
            "task_breakdown",
            request.dict()
        )
        
        return MCPToolCallResponse(
            success=result.get("success", False),
            tool="task_breakdown",
            result=result.get("result"),
            timestamp=result.get("timestamp")
        )
    except Exception as e:
        logger.error(f"Error in AI task breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/motivation", response_model=MCPToolCallResponse)
async def ai_motivation(request: AIMotivationRequest) -> MCPToolCallResponse:
    """Get AI-powered motivation"""
    try:
        from app.core.unified_mcp import unified_mcp
        
        result = await unified_mcp.call_tool(
            "motivation_coach",
            request.dict()
        )
        
        return MCPToolCallResponse(
            success=result.get("success", False),
            tool="motivation_coach",
            result=result.get("result"),
            timestamp=result.get("timestamp")
        )
    except Exception as e:
        logger.error(f"Error in AI motivation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/ritual-suggestion", response_model=MCPToolCallResponse)
async def ai_ritual_suggestion(request: AIRitualRequest) -> MCPToolCallResponse:
    """Get AI ritual suggestions"""
    try:
        from app.core.unified_mcp import unified_mcp
        
        result = await unified_mcp.call_tool(
            "ritual_suggestion",
            request.dict()
        )
        
        return MCPToolCallResponse(
            success=result.get("success", False),
            tool="ritual_suggestion",
            result=result.get("result"),
            timestamp=result.get("timestamp")
        )
    except Exception as e:
        logger.error(f"Error in AI ritual suggestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
