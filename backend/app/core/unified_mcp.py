"""
Unified MCP System for FocusForge
Consolidates all functionality into a single, coherent MCP-based architecture
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Import services
from app.services.task_service import TaskService
from app.services.mood_service import MoodService
from app.services.store_service import StoreService
from app.services.spotify_service import SpotifyService
from app.services.analytics_service import AnalyticsService
from app.services.llm_service import LLMService
from app.services.calendar_service import calendar_service
from app.core.database import get_database
from app.core.memory import memory_manager

logger = logging.getLogger(__name__)


class MCPToolCategory(Enum):
    """Categories of MCP tools"""
    AI_AGENTS = "ai_agents"
    TASK_MANAGEMENT = "task_management"
    MOOD_TRACKING = "mood_tracking"
    GAMIFICATION = "gamification"
    INTEGRATIONS = "integrations"


@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    category: MCPToolCategory
    parameters: Dict[str, Any]
    handler: callable


class UnifiedMCPSystem:
    """
    Unified MCP system that consolidates all functionality into a single,
    coherent architecture based on the Model Context Protocol
    """
    
    def __init__(self):
        self.db = None
        self.services = {}
        self.tools = {}
        self.is_initialized = False
        self._register_all_tools()
    
    async def initialize(self):
        """Initialize the unified MCP system"""
        if self.is_initialized:
            return
        
        try:
            # Initialize database
            self.db = await get_database()
            
            # Initialize all services
            self.services = {
                "task": TaskService(self.db),
                "mood": MoodService(self.db),
                "store": StoreService(self.db),
                "spotify": SpotifyService(),
                "analytics": AnalyticsService(self.db),
                "llm": LLMService()
            }
            
            self.is_initialized = True
            logger.info("Unified MCP system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Unified MCP system: {e}")
            raise
    
    def _register_all_tools(self):
        """Register all MCP tools"""
        
        # AI Agent Tools
        self._register_ai_agent_tools()
        
        # Task Management Tools
        self._register_task_management_tools()
        
        # Mood Tracking Tools
        self._register_mood_tracking_tools()
        
        # Gamification Tools
        self._register_gamification_tools()
        
        # Integration Tools
        self._register_integration_tools()
    
    def _register_ai_agent_tools(self):
        """Register AI agent tools"""
        ai_tools = [
            MCPTool(
                name="task_breakdown",
                description="Break down complex tasks into manageable blocks using AI",
                category=MCPToolCategory.AI_AGENTS,
                parameters={
                    "title": {"type": "string", "required": True},
                    "description": {"type": "string", "required": False},
                    "duration_minutes": {"type": "integer", "required": True},
                    "user_context": {"type": "object", "required": False}
                },
                handler=self._handle_task_breakdown
            ),
            MCPTool(
                name="task_analysis",
                description="Analyze task complexity and provide recommendations",
                category=MCPToolCategory.AI_AGENTS,
                parameters={
                    "title": {"type": "string", "required": True},
                    "description": {"type": "string", "required": False},
                    "duration_minutes": {"type": "integer", "required": True},
                    "user_skill_level": {"type": "string", "required": False}
                },
                handler=self._handle_task_analysis
            ),
            MCPTool(
                name="ai_proof_validation",
                description="Validate task completion proof using AI",
                category=MCPToolCategory.AI_AGENTS,
                parameters={
                    "task_description": {"type": "string", "required": True},
                    "proof_text": {"type": "string", "required": True},
                    "completion_criteria": {"type": "string", "required": False}
                },
                handler=self._handle_ai_proof_validation
            ),
            MCPTool(
                name="motivation_coach",
                description="Get personalized motivational support",
                category=MCPToolCategory.AI_AGENTS,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "current_mood": {"type": "string", "required": False},
                    "challenge": {"type": "string", "required": False},
                    "context": {"type": "object", "required": False}
                },
                handler=self._handle_motivation_coach
            ),
            MCPTool(
                name="proof_validation",
                description="Validate task completion proof using AI",
                category=MCPToolCategory.AI_AGENTS,
                parameters={
                    "task_description": {"type": "string", "required": True},
                    "proof_text": {"type": "string", "required": True},
                    "completion_criteria": {"type": "string", "required": False}
                },
                handler=self._handle_proof_validation
            ),
            MCPTool(
                name="ai_ritual_suggestion",
                description="Get personalized productivity ritual recommendations",
                category=MCPToolCategory.AI_AGENTS,
                parameters={
                    "user_mood": {"type": "string", "required": True},
                    "task_type": {"type": "string", "required": True},
                    "time_of_day": {"type": "string", "required": False},
                    "preferences": {"type": "object", "required": False}
                },
                handler=self._handle_ritual_suggestion
            )
        ]
        
        for tool in ai_tools:
            self.tools[tool.name] = tool
    
    def _register_task_management_tools(self):
        """Register task management tools"""
        task_tools = [
            MCPTool(
                name="create_task",
                description="Create a new task with AI breakdown",
                category=MCPToolCategory.TASK_MANAGEMENT,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "title": {"type": "string", "required": True},
                    "description": {"type": "string", "required": False},
                    "duration_minutes": {"type": "integer", "required": True},
                    "auto_breakdown": {"type": "boolean", "required": False}
                },
                handler=self._handle_create_task
            ),
            MCPTool(
                name="get_tasks",
                description="Get user tasks with optional filtering",
                category=MCPToolCategory.TASK_MANAGEMENT,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "status": {"type": "string", "required": False},
                    "limit": {"type": "integer", "required": False}
                },
                handler=self._handle_get_tasks
            ),
            MCPTool(
                name="start_task_block",
                description="Start working on a specific task block",
                category=MCPToolCategory.TASK_MANAGEMENT,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "block_id": {"type": "string", "required": True}
                },
                handler=self._handle_start_task_block
            ),
            MCPTool(
                name="complete_task_block",
                description="Complete a task block with proof validation",
                category=MCPToolCategory.TASK_MANAGEMENT,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "block_id": {"type": "string", "required": True},
                    "proof_data": {"type": "object", "required": False}
                },
                handler=self._handle_complete_task_block
            ),
            MCPTool(
                name="get_user_dashboard",
                description="Get comprehensive user dashboard data",
                category=MCPToolCategory.TASK_MANAGEMENT,
                parameters={
                    "user_id": {"type": "string", "required": True}
                },
                handler=self._handle_get_user_dashboard
            )
        ]
        
        for tool in task_tools:
            self.tools[tool.name] = tool
    
    def _register_mood_tracking_tools(self):
        """Register mood tracking tools"""
        mood_tools = [
            MCPTool(
                name="log_mood",
                description="Log user mood with context and insights",
                category=MCPToolCategory.MOOD_TRACKING,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "feeling": {"type": "string", "required": True},
                    "intensity": {"type": "integer", "required": False},
                    "note": {"type": "string", "required": False},
                    "context": {"type": "object", "required": False}
                },
                handler=self._handle_log_mood
            ),
            MCPTool(
                name="mood_analysis",
                description="Analyze user mood patterns and trends",
                category=MCPToolCategory.MOOD_TRACKING,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "days_back": {"type": "integer", "required": False}
                },
                handler=self._handle_mood_analysis
            )
        ]
        
        for tool in mood_tools:
            self.tools[tool.name] = tool
    
    def _register_gamification_tools(self):
        """Register gamification tools"""
        gamification_tools = [
            MCPTool(
                name="get_user_profile",
                description="Get user profile with currency and stats",
                category=MCPToolCategory.GAMIFICATION,
                parameters={
                    "user_id": {"type": "string", "required": True}
                },
                handler=self._handle_get_user_profile
            ),
            MCPTool(
                name="award_points",
                description="Award points to user for achievements",
                category=MCPToolCategory.GAMIFICATION,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "points": {"type": "integer", "required": True},
                    "reason": {"type": "string", "required": True}
                },
                handler=self._handle_award_points
            ),
            MCPTool(
                name="redeem_reward",
                description="Redeem store item with user points",
                category=MCPToolCategory.GAMIFICATION,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "item_id": {"type": "string", "required": True}
                },
                handler=self._handle_redeem_reward
            )
        ]
        
        for tool in gamification_tools:
            self.tools[tool.name] = tool
    
    def _register_integration_tools(self):
        """Register integration tools"""
        integration_tools = [
            MCPTool(
                name="play_spotify_playlist",
                description="Play Spotify playlist for focus session",
                category=MCPToolCategory.INTEGRATIONS,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "playlist_id": {"type": "string", "required": True},
                    "device_id": {"type": "string", "required": False}
                },
                handler=self._handle_play_spotify_playlist
            ),
            MCPTool(
                name="add_calendar_event",
                description="Add calendar event for task scheduling",
                category=MCPToolCategory.INTEGRATIONS,
                parameters={
                    "user_id": {"type": "string", "required": True},
                    "title": {"type": "string", "required": True},
                    "start_time": {"type": "string", "required": True},
                    "end_time": {"type": "string", "required": True},
                    "metadata": {"type": "object", "required": False}
                },
                handler=self._handle_add_calendar_event
            )
        ]
        
        for tool in integration_tools:
            self.tools[tool.name] = tool
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        if not self.is_initialized:
            await self.initialize()
        
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }
        
        tool = self.tools[tool_name]
        
        try:
            # Validate parameters
            self._validate_parameters(tool, parameters)
            
            # Call the handler
            result = await tool.handler(parameters)
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_parameters(self, tool: MCPTool, parameters: Dict[str, Any]):
        """Validate tool parameters"""
        for param_name, param_config in tool.parameters.items():
            if param_config.get("required", False) and param_name not in parameters:
                raise ValueError(f"Required parameter '{param_name}' missing for tool '{tool.name}'")
    
    def get_available_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available tools organized by category"""
        tools_by_category = {}
        
        for tool in self.tools.values():
            category = tool.category.value
            if category not in tools_by_category:
                tools_by_category[category] = []
            
            tools_by_category[category].append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            })
        
        return tools_by_category
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "initialized": self.is_initialized,
            "tools_count": len(self.tools),
            "services_available": list(self.services.keys()) if self.services else [],
            "categories": list(MCPToolCategory),
            "tools_by_category": {
                category.value: [
                    tool.name for tool in self.tools.values() 
                    if tool.category == category
                ]
                for category in MCPToolCategory
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # ===== TOOL HANDLERS =====
    
    async def _handle_task_breakdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task breakdown AI agent"""
        llm_service = self.services["llm"]
        
        result = await llm_service.decompose_task_detailed(
            task_description=params["title"],
            duration_minutes=params["duration_minutes"],
            user_context=params.get("user_context", {})
        )
        
        return {
            "blocks": result,
            "total_blocks": len(result),
            "estimated_duration": params["duration_minutes"]
        }
    
    async def _handle_task_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task analysis AI agent"""
        llm_service = self.services["llm"]
        
        analysis = await llm_service.get_task_analysis(
            task_title=params["title"],
            description=params.get("description", ""),
            duration_minutes=params["duration_minutes"],
            user_skill_level=params.get("user_skill_level", "intermediate")
        )
        
        return analysis
    
    async def _handle_motivation_coach(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle motivation coach AI agent"""
        llm_service = self.services["llm"]
        
        motivation = await llm_service.get_motivational_message(
            user_context=params.get("context", {}),
            mood=params.get("current_mood", "neutral"),
            current_challenge=params.get("challenge", "")
        )
        
        return {
            "message": motivation,
            "user_id": params["user_id"],
            "mood": params.get("current_mood", "neutral")
        }
    
    async def _handle_ai_proof_validation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI proof validation"""
        llm_service = self.services["llm"]
        
        validation = await llm_service.validate_task_proof(
            task_description=params["task_description"],
            proof_text=params["proof_text"],
            completion_criteria=params.get("completion_criteria", "")
        )
        
        return validation
    
    async def _handle_proof_validation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle proof validation AI agent"""
        llm_service = self.services["llm"]
        
        validation = await llm_service.validate_task_proof(
            task_description=params["task_description"],
            proof_text=params["proof_text"],
            completion_criteria=params.get("completion_criteria", "")
        )
        
        return validation
    
    async def _handle_ritual_suggestion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ritual suggestion AI agent"""
        llm_service = self.services["llm"]
        
        suggestions = await llm_service.suggest_productivity_ritual(
            user_mood=params["user_mood"],
            task_type=params["task_type"],
            time_of_day=params.get("time_of_day", "morning"),
            preferences=params.get("preferences", {})
        )
        
        return suggestions
    
    async def _handle_create_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task creation"""
        task_service = self.services["task"]
        
        # Create basic task
        from app.models.schemas import TaskCreate
        task_data = TaskCreate(
            title=params["title"],
            description=params.get("description", ""),
            estimated_minutes=params["duration_minutes"]
        )
        
        task = await task_service.create_task(params["user_id"], task_data)
        
        # Auto-breakdown if requested
        if params.get("auto_breakdown", True):
            breakdown = await self._handle_task_breakdown({
                "title": params["title"],
                "description": params.get("description", ""),
                "duration_minutes": params["duration_minutes"]
            })
            
            # Create task blocks
            blocks = []
            for i, block_data in enumerate(breakdown["blocks"]):
                block = {
                    "task_id": task["id"],
                    "block_number": i + 1,
                    "title": block_data.get("title", f"Block {i + 1}"),
                    "description": block_data.get("description", ""),
                    "duration_minutes": block_data.get("duration_minutes", 25),
                    "status": "pending"
                }
                blocks.append(block)
            
            task["blocks"] = blocks
            task["breakdown"] = breakdown
        
        return task
    
    async def _handle_get_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting user tasks"""
        task_service = self.services["task"]
        
        tasks = await task_service.get_user_tasks(
            user_id=params["user_id"],
            status=params.get("status"),
            limit=params.get("limit", 10)
        )
        
        return {
            "tasks": tasks,
            "count": len(tasks),
            "user_id": params["user_id"]
        }
    
    async def _handle_start_task_block(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle starting a task block"""
        try:
            # Get the task service
            task_service = self.services["task"]
            
            # Start the task block
            result = await task_service.start_task_block(
                block_id=params["block_id"],
                user_id=params["user_id"]
            )
            
            if result.get("success"):
                return {
                    "status": "started",
                    "block_id": params["block_id"],
                    "start_time": datetime.now().isoformat(),
                    "user_id": params["user_id"],
                    "suggested_break_after": result.get("suggested_break_after", 25),
                    "estimated_tokens": result.get("estimated_tokens", 10)
                }
            else:
                return {
                    "status": "failed",
                    "error": result.get("message", "Unknown error"),
                    "block_id": params["block_id"],
                    "user_id": params["user_id"]
                }
                
        except Exception as e:
            logger.error(f"Error starting task block: {e}")
            return {
                "status": "error",
                "error": str(e),
                "block_id": params["block_id"],
                "user_id": params["user_id"]
            }
    
    async def _handle_complete_task_block(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle completing a task block"""
        try:
            # Get the task service
            task_service = self.services["task"]
            
            # Complete the task block
            result = await task_service.complete_task_block(
                block_id=params["block_id"],
                user_id=params["user_id"],
                proof_data=params.get("proof_data", {})
            )
            
            if result.get("success"):
                return {
                    "status": "completed",
                    "block_id": params["block_id"],
                    "completion_time": datetime.now().isoformat(),
                    "proof_valid": True,
                    "tokens_earned": result.get("tokens_earned", 0),
                    "user_id": params["user_id"],
                    "next_break_minutes": result.get("next_break_minutes", 5)
                }
            else:
                return {
                    "status": "failed",
                    "error": result.get("message", "Unknown error"),
                    "block_id": params["block_id"],
                    "user_id": params["user_id"]
                }
                
        except Exception as e:
            logger.error(f"Error completing task block: {e}")
            return {
                "status": "error",
                "error": str(e),
                "block_id": params["block_id"],
                "user_id": params["user_id"]
            }
    
    async def _handle_get_user_dashboard(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting user dashboard"""
        try:
            user_id = params["user_id"]
            
            # Get tasks
            tasks_result = await self._handle_get_tasks({"user_id": user_id, "limit": 10})
            
            # Get mood analysis
            mood_result = await self._handle_mood_analysis({"user_id": user_id, "days_back": 7})
            
            # Get user profile
            profile_result = await self._handle_get_user_profile({"user_id": user_id})
            
            # Get task service for dashboard
            task_service = self.services["task"]
            dashboard_data = await task_service.get_user_dashboard(user_id)
            
            return {
                "user_id": user_id,
                "tasks": tasks_result,
                "mood_analysis": mood_result,
                "profile": profile_result,
                "dashboard": dashboard_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user dashboard: {e}")
            return {
                "error": str(e),
                "user_id": params["user_id"]
            }
    
    async def _handle_log_mood(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mood logging"""
        mood_service = self.services["mood"]
        
        from app.models.schemas import MoodLogCreate
        mood_data = MoodLogCreate(
            feeling=params["feeling"],
            note=params.get("note", "")
        )
        
        result = await mood_service.log_mood(
            user_id=params["user_id"],
            mood_data=mood_data,
            context=params.get("context", {})
        )
        
        return result
    
    async def _handle_mood_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mood analysis"""
        mood_service = self.services["mood"]
        
        patterns = await mood_service.analyze_mood_patterns(params["user_id"])
        recent_moods = await mood_service.get_mood_for_time_period(
            user_id=params["user_id"],
            hours_back=params.get("days_back", 7) * 24
        )
        
        return {
            "patterns": patterns,
            "recent_moods": recent_moods,
            "analysis_period_days": params.get("days_back", 7)
        }
    
    async def _handle_get_user_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting user profile"""
        try:
            store_service = self.services["store"]
            profile = await store_service.get_user_profile(params["user_id"])
            
            return {
                "user_id": params["user_id"],
                "points": profile.currency,
                "level": profile.stats.get("level", 1),
                "achievements": profile.achievements,
                "total_tasks_completed": profile.stats.get("tasks_completed", 0),
                "current_streak": profile.stats.get("streak_days", 0),
                "total_earned": profile.total_earned,
                "total_spent": profile.total_spent
            }
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {
                "error": str(e),
                "user_id": params["user_id"]
            }
    
    async def _handle_award_points(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle awarding points"""
        try:
            store_service = self.services["store"]
            
            result = await store_service.add_currency(
                user_id=params["user_id"],
                amount=params["points"],
                source="achievement",
                metadata={"reason": params["reason"]}
            )
            
            return {
                "success": result.get("success", False),
                "points_awarded": params["points"],
                "reason": params["reason"],
                "new_total": result.get("new_balance", 0),
                "user_id": params["user_id"]
            }
            
        except Exception as e:
            logger.error(f"Error awarding points: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": params["user_id"]
            }
    
    async def _handle_redeem_reward(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reward redemption"""
        try:
            store_service = self.services["store"]
            
            result = await store_service.purchase_item(
                user_id=params["user_id"],
                item_name=params["item_id"]
            )
            
            return {
                "success": result.get("success", False),
                "item_id": params["item_id"],
                "points_spent": result.get("new_balance", 0),
                "remaining_points": result.get("new_balance", 0),
                "user_id": params["user_id"]
            }
            
        except Exception as e:
            logger.error(f"Error redeeming reward: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": params["user_id"]
            }
    
    async def _handle_play_spotify_playlist(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Spotify playlist playback"""
        try:
            spotify_service = self.services["spotify"]
            
            result = await spotify_service.play_playlist(
                playlist_uri=params["playlist_id"],
                device_id=params.get("device_id", "default")
            )
            
            return {
                "status": "playing" if "✅" in result else "failed",
                "playlist_id": params["playlist_id"],
                "device_id": params.get("device_id", "default"),
                "user_id": params["user_id"],
                "message": result
            }
            
        except Exception as e:
            logger.error(f"Error playing Spotify playlist: {e}")
            return {
                "status": "error",
                "error": str(e),
                "playlist_id": params["playlist_id"],
                "user_id": params["user_id"]
            }
    
    async def _handle_add_calendar_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calendar event creation"""
        try:
            # Use the real calendar service
            event = await calendar_service.create_event(params, params["user_id"])
            
            return {
                "success": True,
                "event_id": event.id,
                "title": event.title,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "user_id": event.user_id,
                "calendar_id": event.calendar_id,
                "location": event.location,
                "attendees": event.attendees,
                "reminders": event.reminders,
                "metadata": event.metadata
            }
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": params["user_id"]
            }


# Global unified MCP system instance
unified_mcp = UnifiedMCPSystem()
