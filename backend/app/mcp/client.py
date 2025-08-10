"""
MCP Client for FocusForge
Integrates Model Context Protocol client capabilities into existing services
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

# Mock MCP imports until library is properly installed
try:
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client
    MCP_LIBRARY_AVAILABLE = True
except ImportError:
    try:
        # Try alternative import structure
        from mcp import ClientSession, StdioServerParameters
        from mcp.client import stdio_client
        MCP_LIBRARY_AVAILABLE = True
    except ImportError:
        MCP_LIBRARY_AVAILABLE = False
        logging.warning("MCP library not available, using mock implementation")
        
        # Create mock classes
        class ClientSession: pass
        class StdioServerParameters: pass
        def stdio_client(*args, **kwargs): pass

logger = logging.getLogger(__name__)

class FocusForgeMCPClient:
    """MCP Client for interacting with FocusForge MCP server and external tools"""
    
    def __init__(self):
        self.session: Optional[Any] = None
        self.connected = False
        self.mock_mode = not MCP_LIBRARY_AVAILABLE
        self.simplified_server = None
        
    async def connect(self, server_path: str = "python backend/app/mcp/server.py"):
        """Connect to the MCP server"""
        if self.mock_mode or not MCP_LIBRARY_AVAILABLE:
            # Use simplified internal server instead of external process
            try:
                from app.mcp.simplified_server import SimplifiedMCPServer
                self.simplified_server = SimplifiedMCPServer()
                await self.simplified_server.start()
                self.connected = True
                logger.info("MCP Client connected to simplified internal server")
                return
            except Exception as e:
                logger.warning(f"Failed to start simplified server: {e}")
                # Fall back to mock mode
                self.connected = True
                logger.info("MCP Client connected (mock mode)")
                return
            
        try:
            if not MCP_LIBRARY_AVAILABLE:
                raise ImportError("MCP library not available")
                
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "app.mcp.server"],  # Fixed module path
                env=None
            )
            
            # Create the session properly
            client_context = stdio_client(server_params)
            read, write = await client_context.__aenter__()
            
            self.session = ClientSession(read, write)
            await self.session.initialize()
            
            self.connected = True
            logger.info("MCP Client connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect MCP client: {e}")
            self.connected = False
            # Fall back to simplified server
            try:
                from app.mcp.simplified_server import SimplifiedMCPServer
                self.simplified_server = SimplifiedMCPServer()
                await self.simplified_server.start()
                self.connected = True
                logger.info("Falling back to simplified internal server")
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                self.mock_mode = True
                self.connected = True
                logger.info("Falling back to mock mode")
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.session:
            await self.session.close()
            self.connected = False
            logger.info("MCP Client disconnected")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server"""
        if not self.connected:
            await self.connect()
        
        # Use simplified server if available
        if self.simplified_server:
            try:
                tools = self.simplified_server.get_available_tools()
                return tools
            except Exception as e:
                logger.error(f"Error getting tools from simplified server: {e}")
        
        if self.mock_mode:
            # Return mock tool list
            return [
                {"name": "task_breakdown", "description": "Break down tasks into manageable steps"},
                {"name": "motivation_coach", "description": "Provide motivational support"},
                {"name": "task_analysis", "description": "Analyze task complexity"},
                {"name": "proof_validation", "description": "Validate task completion proof"},
                {"name": "ritual_suggestion", "description": "Suggest productivity rituals"},
                {"name": "comprehensive_guidance", "description": "Comprehensive AI guidance"},
                {"name": "create_task", "description": "Create new tasks"},
                {"name": "log_mood", "description": "Log mood entries"},
                {"name": "get_focus_playlist", "description": "Get Spotify focus playlist"}
            ]
        
        try:
            if not self.session:
                raise Exception("No active MCP session")
                
            tools_result = await self.session.list_tools()
            return [tool.model_dump() for tool in tools_result.tools]
        except Exception as e:
            logger.error(f"Error listing MCP tools: {e}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool via MCP"""
        if not self.connected:
            await self.connect()
        
        # Use simplified server if available
        if self.simplified_server:
            try:
                result = await self.simplified_server.call_tool(name, arguments)
                return result
            except Exception as e:
                logger.error(f"Simplified server error: {e}")
                # Fall back to mock
                return self._mock_tool_response(name, arguments)
        
        if self.mock_mode:
            # Return mock responses for testing
            return self._mock_tool_response(name, arguments)
        
        try:
            if not self.session:
                raise Exception("No active MCP session")
                
            result = await self.session.call_tool(name, arguments)
            
            # Parse the response
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)
            
            return {"success": False, "error": "No content in response"}
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {name}: {e}")
            return {"success": False, "error": str(e)}
    
    def _mock_tool_response(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock responses for testing without MCP library"""
        mock_responses = {
            "task_breakdown": {
                "success": True,
                "breakdown": [
                    {"step": 1, "title": "Plan the task", "duration": 5},
                    {"step": 2, "title": "Execute main work", "duration": 15},
                    {"step": 3, "title": "Review and finalize", "duration": 5}
                ],
                "tool": "task_breakdown",
                "mock": True
            },
            "motivation_coach": {
                "success": True,
                "motivation": "You've got this! Break it down into small steps and celebrate each win.",
                "tool": "motivation_coach", 
                "mock": True
            },
            "create_task": {
                "success": True,
                "task_id": f"mock_task_{arguments.get('title', 'untitled').lower().replace(' ', '_')}",
                "tool": "create_task",
                "mock": True
            },
            "log_mood": {
                "success": True,
                "logged": True,
                "mood_id": f"mock_mood_{datetime.now().isoformat()}",
                "tool": "log_mood",
                "mock": True
            }
        }
        
        return mock_responses.get(name, {
            "success": True,
            "result": f"Mock response for {name}",
            "arguments": arguments,
            "tool": name,
            "mock": True
        })
    
    # ===== AI AGENT TOOLS =====
    
    async def get_task_breakdown(self, title: str, description: str = "", 
                               duration_minutes: int = 25, 
                               user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get AI task breakdown via MCP"""
        return await self.call_tool("task_breakdown", {
            "title": title,
            "description": description,
            "duration_minutes": duration_minutes,
            "user_context": user_context or {}
        })
    
    async def get_task_analysis(self, title: str, description: str = "",
                              duration_minutes: int = 25,
                              user_skill_level: str = "intermediate") -> Dict[str, Any]:
        """Get AI task analysis via MCP"""
        return await self.call_tool("task_analysis", {
            "title": title,
            "description": description,
            "duration_minutes": duration_minutes,
            "user_skill_level": user_skill_level
        })
    
    async def get_motivation(self, user_id: str, current_mood: str = "neutral",
                           challenge: str = "", context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get motivational support via MCP"""
        return await self.call_tool("motivation_coach", {
            "user_id": user_id,
            "current_mood": current_mood,
            "challenge": challenge,
            "context": context or {}
        })
    
    async def validate_proof(self, task_description: str, proof_text: str,
                           completion_criteria: str = "") -> Dict[str, Any]:
        """Validate task proof via MCP"""
        return await self.call_tool("proof_validation", {
            "task_description": task_description,
            "proof_text": proof_text,
            "completion_criteria": completion_criteria
        })
    
    async def get_ritual_suggestion(self, user_mood: str, task_type: str,
                                  time_of_day: str = "morning",
                                  preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """Get ritual suggestions via MCP"""
        return await self.call_tool("ritual_suggestion", {
            "user_mood": user_mood,
            "task_type": task_type,
            "time_of_day": time_of_day,
            "preferences": preferences or {}
        })
    
    async def get_comprehensive_guidance(self, user_id: str, task_data: Dict[str, Any],
                                       user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get comprehensive AI guidance via MCP"""
        return await self.call_tool("comprehensive_guidance", {
            "user_id": user_id,
            "task_data": task_data,
            "user_context": user_context
        })
    
    # ===== TASK MANAGEMENT TOOLS =====
    
    async def create_task(self, user_id: str, title: str, description: str = "",
                         duration_minutes: int = 25, auto_breakdown: bool = True) -> Dict[str, Any]:
        """Create task via MCP"""
        return await self.call_tool("create_task", {
            "user_id": user_id,
            "title": title,
            "description": description,
            "duration_minutes": duration_minutes,
            "auto_breakdown": auto_breakdown
        })
    
    async def get_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get user dashboard via MCP"""
        return await self.call_tool("get_user_dashboard", {
            "user_id": user_id
        })
    
    async def start_block(self, user_id: str, block_id: str) -> Dict[str, Any]:
        """Start task block via MCP"""
        return await self.call_tool("start_task_block", {
            "user_id": user_id,
            "block_id": block_id
        })
    
    async def complete_block(self, user_id: str, block_id: str,
                           proof_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Complete task block via MCP"""
        return await self.call_tool("complete_task_block", {
            "user_id": user_id,
            "block_id": block_id,
            "proof_data": proof_data
        })
    
    # ===== MOOD MANAGEMENT TOOLS =====
    
    async def log_mood(self, user_id: str, feeling: str, intensity: int = 5,
                      note: str = "", context: Optional[Dict] = None) -> Dict[str, Any]:
        """Log mood via MCP"""
        return await self.call_tool("log_mood", {
            "user_id": user_id,
            "feeling": feeling,
            "intensity": intensity,
            "note": note,
            "context": context or {}
        })
    
    async def analyze_mood(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Analyze mood patterns via MCP"""
        return await self.call_tool("mood_analysis", {
            "user_id": user_id,
            "days_back": days_back
        })
    
    # ===== STORE/GAMIFICATION TOOLS =====
    
    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile via MCP"""
        return await self.call_tool("get_user_profile", {
            "user_id": user_id
        })
    
    async def purchase_item(self, user_id: str, item_id: str, quantity: int = 1) -> Dict[str, Any]:
        """Purchase store item via MCP"""
        return await self.call_tool("purchase_item", {
            "user_id": user_id,
            "item_id": item_id,
            "quantity": quantity
        })
    
    # ===== SPOTIFY INTEGRATION TOOLS =====
    
    async def get_focus_playlist(self, mood: str = "focus", duration_minutes: int = 25,
                               genre_preference: str = "") -> Dict[str, Any]:
        """Get focus playlist via MCP"""
        return await self.call_tool("get_focus_playlist", {
            "mood": mood,
            "duration_minutes": duration_minutes,
            "genre_preference": genre_preference
        })

# Global MCP client instance
mcp_client = FocusForgeMCPClient()

async def get_mcp_client() -> FocusForgeMCPClient:
    """Get the global MCP client instance"""
    if not mcp_client.connected:
        await mcp_client.connect()
    return mcp_client

# Context manager for MCP operations
class MCPSession:
    """Context manager for MCP operations"""
    
    def __init__(self):
        self.client = None
    
    async def __aenter__(self) -> FocusForgeMCPClient:
        self.client = await get_mcp_client()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Keep connection alive for reuse
        pass
