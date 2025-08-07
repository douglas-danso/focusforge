"""
FocusForge MCP Server
Model Context Protocol server for enhanced AI agent interactions
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    JSONValue,
    EmbeddedResource,
    ErrorData,
    McpError,
)

from app.services.task_service import TaskService
from app.services.mood_service import MoodService
from app.services.llm_service import LLMService
from app.services.store_service import StoreService
from app.services.spotify_service import SpotifyService
from app.core.database import get_database

logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server for FocusForge productivity tools and AI agents"""
    
    def __init__(self):
        self.server = Server("focusforge-mcp")
        self.db = None
        self.services = {}
        
        # Register tools
        self._register_tools()
        
    async def initialize_services(self):
        """Initialize database and services"""
        try:
            self.db = await get_database()
            self.services = {
                "task": TaskService(self.db),
                "mood": MoodService(self.db),
                "llm": LLMService(),
                "store": StoreService(self.db),
                "spotify": SpotifyService()
            }
            logger.info("MCP Server services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MCP services: {e}")
            raise
    
    def _register_tools(self):
        """Register all available MCP tools"""
        
        # Task Management Tools
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    # Task Breakdown Agent
                    Tool(
                        name="task_breakdown",
                        description="Break down a complex task into manageable blocks using AI",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Task title"},
                                "description": {"type": "string", "description": "Task description"},
                                "duration_minutes": {"type": "integer", "description": "Total duration in minutes"},
                                "user_context": {"type": "object", "description": "User context for personalization"}
                            },
                            "required": ["title", "duration_minutes"]
                        }
                    ),
                    
                    # Task Analysis Agent
                    Tool(
                        name="task_analysis",
                        description="Analyze task difficulty and provide recommendations",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "duration_minutes": {"type": "integer"},
                                "user_skill_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]}
                            },
                            "required": ["title", "duration_minutes"]
                        }
                    ),
                    
                    # Motivation Coach Agent
                    Tool(
                        name="motivation_coach",
                        description="Get personalized motivational support",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "current_mood": {"type": "string"},
                                "challenge": {"type": "string"},
                                "context": {"type": "object"}
                            },
                            "required": ["user_id"]
                        }
                    ),
                    
                    # Proof Verification Agent
                    Tool(
                        name="proof_validation",
                        description="Validate task completion proof using AI",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "task_description": {"type": "string"},
                                "proof_text": {"type": "string"},
                                "completion_criteria": {"type": "string"}
                            },
                            "required": ["task_description", "proof_text"]
                        }
                    ),
                    
                    # Ritual Advisor Agent
                    Tool(
                        name="ritual_suggestion",
                        description="Get personalized productivity ritual recommendations",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_mood": {"type": "string"},
                                "task_type": {"type": "string"},
                                "time_of_day": {"type": "string"},
                                "preferences": {"type": "object"}
                            },
                            "required": ["user_mood", "task_type"]
                        }
                    ),
                    
                    # Mood Management Tools
                    Tool(
                        name="mood_analysis",
                        description="Analyze user mood patterns and trends",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "days_back": {"type": "integer", "default": 30}
                            },
                            "required": ["user_id"]
                        }
                    ),
                    
                    Tool(
                        name="log_mood",
                        description="Log user mood with context and insights",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "feeling": {"type": "string"},
                                "intensity": {"type": "integer", "minimum": 1, "maximum": 10},
                                "note": {"type": "string"},
                                "context": {"type": "object"}
                            },
                            "required": ["user_id", "feeling"]
                        }
                    ),
                    
                    # Task Management Tools
                    Tool(
                        name="create_task",
                        description="Create a new task with AI breakdown",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "duration_minutes": {"type": "integer"},
                                "auto_breakdown": {"type": "boolean", "default": True}
                            },
                            "required": ["user_id", "title", "duration_minutes"]
                        }
                    ),
                    
                    Tool(
                        name="get_user_dashboard",
                        description="Get comprehensive user dashboard data",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"}
                            },
                            "required": ["user_id"]
                        }
                    ),
                    
                    Tool(
                        name="start_task_block",
                        description="Start working on a specific task block",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "block_id": {"type": "string"}
                            },
                            "required": ["user_id", "block_id"]
                        }
                    ),
                    
                    Tool(
                        name="complete_task_block",
                        description="Complete a task block with proof validation",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "block_id": {"type": "string"},
                                "proof_data": {"type": "object"}
                            },
                            "required": ["user_id", "block_id"]
                        }
                    ),
                    
                    # Store/Gamification Tools
                    Tool(
                        name="get_user_profile",
                        description="Get user profile with currency and stats",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"}
                            },
                            "required": ["user_id"]
                        }
                    ),
                    
                    Tool(
                        name="purchase_item",
                        description="Purchase an item from the store",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "item_id": {"type": "string"},
                                "quantity": {"type": "integer", "default": 1}
                            },
                            "required": ["user_id", "item_id"]
                        }
                    ),
                    
                    # Spotify Integration Tools
                    Tool(
                        name="get_focus_playlist",
                        description="Get Spotify playlists for focus sessions",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "mood": {"type": "string"},
                                "duration_minutes": {"type": "integer"},
                                "genre_preference": {"type": "string"}
                            }
                        }
                    ),
                    
                    # Comprehensive Agent Coordination
                    Tool(
                        name="comprehensive_guidance",
                        description="Get guidance from all AI agents working together",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "task_data": {"type": "object"},
                                "user_context": {"type": "object"}
                            },
                            "required": ["user_id", "task_data"]
                        }
                    )
                ]
            )
        
        # Tool Handlers
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Optional[dict]
        ) -> CallToolResult:
            try:
                if not self.services:
                    await self.initialize_services()
                
                result = await self._execute_tool(name, arguments or {})
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(result, indent=2, default=str)
                        )
                    ]
                )
                
            except Exception as e:
                logger.error(f"Tool execution error for {name}: {e}")
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", 
                            text=json.dumps({
                                "error": str(e),
                                "tool": name,
                                "success": False
                            })
                        )
                    ],
                    isError=True
                )
    
    async def _execute_tool(self, name: str, arguments: dict) -> dict:
        """Execute a specific tool"""
        
        # Task Breakdown Agent
        if name == "task_breakdown":
            detailed_breakdown = await self.services["llm"].decompose_task_detailed(
                f"{arguments['title']}: {arguments.get('description', '')}",
                arguments["duration_minutes"],
                arguments.get("user_context")
            )
            return {
                "success": True,
                "breakdown": detailed_breakdown,
                "tool": "task_breakdown"
            }
        
        # Task Analysis Agent
        elif name == "task_analysis":
            analysis = await self.services["llm"].get_task_analysis(
                task_title=arguments["title"],
                description=arguments.get("description", ""),
                duration_minutes=arguments["duration_minutes"],
                user_skill_level=arguments.get("user_skill_level", "intermediate")
            )
            return {
                "success": True,
                "analysis": analysis,
                "tool": "task_analysis"
            }
        
        # Motivation Coach Agent
        elif name == "motivation_coach":
            user_context = await self.services["task"]._get_user_context(arguments["user_id"])
            
            motivation = await self.services["llm"].get_motivational_message(
                user_context=user_context,
                mood=arguments.get("current_mood", user_context.get("current_mood", "neutral")),
                current_challenge=arguments.get("challenge", "")
            )
            return {
                "success": True,
                "motivation": motivation,
                "tool": "motivation_coach"
            }
        
        # Proof Validation Agent
        elif name == "proof_validation":
            validation = await self.services["llm"].validate_task_proof(
                task_description=arguments["task_description"],
                proof_text=arguments["proof_text"],
                completion_criteria=arguments.get("completion_criteria", "")
            )
            return {
                "success": True,
                "validation": validation,
                "tool": "proof_validation"
            }
        
        # Ritual Advisor Agent
        elif name == "ritual_suggestion":
            ritual = await self.services["llm"].suggest_ritual(
                user_mood=arguments["user_mood"],
                task_type=arguments["task_type"],
                time_of_day=arguments.get("time_of_day", "morning"),
                user_preferences=arguments.get("preferences", {})
            )
            return {
                "success": True,
                "ritual": ritual,
                "tool": "ritual_suggestion"
            }
        
        # Mood Analysis
        elif name == "mood_analysis":
            patterns = await self.services["mood"].analyze_mood_patterns(arguments["user_id"])
            trends = await self.services["mood"].get_mood_trends(
                arguments["user_id"], 
                arguments.get("days_back", 30)
            )
            return {
                "success": True,
                "patterns": patterns,
                "trends": trends,
                "tool": "mood_analysis"
            }
        
        # Log Mood
        elif name == "log_mood":
            from app.models.schemas import MoodLogCreate
            
            mood_data = MoodLogCreate(
                feeling=arguments["feeling"],
                note=arguments.get("note", "")
            )
            
            result = await self.services["mood"].log_mood(
                user_id=arguments["user_id"],
                mood_data=mood_data,
                context=arguments.get("context", {})
            )
            return {
                "success": True,
                "mood_log": result,
                "tool": "log_mood"
            }
        
        # Create Task
        elif name == "create_task":
            from app.models.schemas import TaskCreate
            
            task_data = TaskCreate(
                title=arguments["title"],
                description=arguments.get("description", ""),
                duration_minutes=arguments["duration_minutes"]
            )
            
            result = await self.services["task"].create_task(
                user_id=arguments["user_id"],
                task_data=task_data,
                auto_breakdown=arguments.get("auto_breakdown", True)
            )
            return {
                "success": result["success"],
                "task": result,
                "tool": "create_task"
            }
        
        # Get User Dashboard
        elif name == "get_user_dashboard":
            dashboard = await self.services["task"].get_user_dashboard(arguments["user_id"])
            return {
                "success": True,
                "dashboard": dashboard,
                "tool": "get_user_dashboard"
            }
        
        # Start Task Block
        elif name == "start_task_block":
            result = await self.services["task"].start_task_block(
                block_id=arguments["block_id"],
                user_id=arguments["user_id"]
            )
            return {
                "success": result["success"],
                "result": result,
                "tool": "start_task_block"
            }
        
        # Complete Task Block
        elif name == "complete_task_block":
            result = await self.services["task"].complete_task_block(
                block_id=arguments["block_id"],
                user_id=arguments["user_id"],
                proof_data=arguments.get("proof_data")
            )
            return {
                "success": result["success"],
                "result": result,
                "tool": "complete_task_block"
            }
        
        # Get User Profile
        elif name == "get_user_profile":
            profile = await self.services["store"].get_user_profile(arguments["user_id"])
            return {
                "success": True,
                "profile": profile,
                "tool": "get_user_profile"
            }
        
        # Purchase Item
        elif name == "purchase_item":
            result = await self.services["store"].purchase_item(
                user_id=arguments["user_id"],
                item_id=arguments["item_id"],
                quantity=arguments.get("quantity", 1)
            )
            return {
                "success": result["success"],
                "purchase": result,
                "tool": "purchase_item"
            }
        
        # Get Focus Playlist
        elif name == "get_focus_playlist":
            playlists = await self.services["spotify"].get_focus_playlists(
                mood=arguments.get("mood", "focus"),
                duration=arguments.get("duration_minutes", 25)
            )
            return {
                "success": True,
                "playlists": playlists,
                "tool": "get_focus_playlist"
            }
        
        # Comprehensive Guidance
        elif name == "comprehensive_guidance":
            user_context = await self.services["task"]._get_user_context(arguments["user_id"])
            
            guidance = await self.services["llm"].get_comprehensive_task_guidance(
                task_data=arguments["task_data"],
                user_context=arguments.get("user_context", user_context)
            )
            return {
                "success": guidance["success"],
                "guidance": guidance,
                "tool": "comprehensive_guidance"
            }
        
        else:
            raise ValueError(f"Unknown tool: {name}")

# Alias for backward compatibility
FocusForgeMCPServer = MCPServer

async def main():
    """Run the MCP server"""
    mcp_server = MCPServer()
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="focusforge-mcp",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
