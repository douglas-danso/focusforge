"""
Memory-Chain-Planner Orchestrator
Central coordinator that integrates memory, chains, and planner with MCP
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

from app.core.memory import memory_manager, MemoryType
from app.core.chains import chain_executor
from app.core.planner import action_planner, ActionType, ActionPriority
from app.core.unified_mcp import unified_mcp
from app.core.config import settings

logger = logging.getLogger(__name__)


class MCPOrchestrator:
    """
    Central orchestrator that implements the Memory-Chain-Planner pattern
    Coordinates between memory, chains, planner, and MCP system
    """
    
    def __init__(self):
        self.initialized = False
        self.background_tasks = set()
        self.event_handlers = {}
        self.processing_queue = asyncio.Queue()
        self.is_processing = False
    
    async def initialize(self):
        """Initialize the orchestrator and all components"""
        if self.initialized:
            return
        
        logger.info("Initializing Memory-Chain-Planner orchestrator...")
        
        try:
            # Initialize memory system
            await memory_manager.initialize()
            logger.info("Memory system initialized")
            
            # Initialize unified MCP
            await unified_mcp.initialize()
            logger.info("Unified MCP system initialized")
            
            # Start background processing
            await self._start_background_processing()
            
            self.initialized = True
            logger.info("Memory-Chain-Planner orchestrator fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    
    async def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        logger.info("Shutting down Memory-Chain-Planner orchestrator...")
        
        self.is_processing = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("Orchestrator shutdown complete")
    
    # ===== HIGH-LEVEL WORKFLOW METHODS =====
    
    async def handle_task_creation(self, user_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle complete task creation workflow
        Implements the Memory-Chain-Planner pattern for task creation
        """
        logger.info(f"Handling task creation for user {user_id}")
        
        try:
            # 1. MEMORY: Store user context and retrieve relevant history
            await self._update_user_context(user_id, {
                "last_task_creation": datetime.now().isoformat(),
                "task_preferences": task_data.get("preferences", {})
            })
            
            user_context = await memory_manager.get_user_context(user_id)
            similar_tasks = await memory_manager.search_similar_tasks(
                user_id, 
                task_data.get("description", ""), 
                limit=3
            )
            
            # 2. CHAINS: Execute task analysis and breakdown
            analysis_result = await chain_executor.execute_chain(
                "task_analysis",
                {
                    "title": task_data.get("title", ""),
                    "description": task_data.get("description", ""),
                    "duration_minutes": task_data.get("duration_minutes", 60),
                    "skill_level": task_data.get("skill_level", "intermediate")
                },
                user_id
            )
            
            breakdown_result = await chain_executor.execute_chain(
                "task_breakdown",
                {
                    "title": task_data.get("title", ""),
                    "description": task_data.get("description", ""),
                    "duration_minutes": task_data.get("duration_minutes", 60)
                },
                user_id
            )
            
            # 3. PLANNER: Create execution plan
            planned_actions = await action_planner.plan_task_creation(user_id, task_data)
            
            # 4. MCP: Create the task using unified MCP
            mcp_result = await unified_mcp.call_tool(
                "create_task",
                {
                    "user_id": user_id,
                    "title": task_data.get("title", ""),
                    "description": task_data.get("description", ""),
                    "duration_minutes": task_data.get("duration_minutes", 60),
                    "auto_breakdown": True
                }
            )
            
            # 5. MEMORY: Store the complete workflow result
            workflow_result = {
                "user_context": user_context,
                "similar_tasks": similar_tasks,
                "analysis": analysis_result.get("output", {}),
                "breakdown": breakdown_result.get("output", {}),
                "planned_actions": planned_actions,
                "mcp_result": mcp_result,
                "created_at": datetime.now().isoformat()
            }
            
            await memory_manager.store_task_insights(
                user_id,
                mcp_result.get("result", {}).get("id", "unknown"),
                workflow_result
            )
            
            # 6. PLANNER: Execute immediate actions
            await action_planner.execute_ready_actions(user_id, max_actions=2)
            
            return {
                "success": True,
                "task": mcp_result.get("result", {}),
                "analysis": analysis_result.get("output", {}),
                "breakdown": breakdown_result.get("output", {}),
                "planned_actions": len(planned_actions),
                "user_context_enhanced": bool(user_context),
                "similar_tasks_found": len(similar_tasks)
            }
            
        except Exception as e:
            logger.error(f"Task creation workflow failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_task_completion(self, user_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle complete task completion workflow
        """
        logger.info(f"Handling task completion for user {user_id}")
        
        try:
            # 1. MEMORY: Retrieve task context and user history
            task_id = completion_data.get("task_id", "")
            task_insights = await memory_manager.get_task_insights(user_id, task_id)
            user_context = await memory_manager.get_user_context(user_id)
            
            # 2. CHAINS: Validate proof if provided
            validation_result = None
            if completion_data.get("proof_text"):
                validation_result = await chain_executor.execute_chain(
                    "proof_validation",
                    {
                        "task_description": completion_data.get("task_description", ""),
                        "completion_criteria": completion_data.get("completion_criteria", ""),
                        "proof_text": completion_data.get("proof_text", "")
                    },
                    user_id
                )
            
            # 3. CHAINS: Generate celebration motivation
            motivation_result = await chain_executor.execute_chain(
                "motivation",
                {
                    "mood": "high",
                    "challenge": "",
                    "accomplishments": [completion_data.get("task_title", "")]
                },
                user_id
            )
            
            # 4. MCP: Complete the task and award points
            complete_result = await unified_mcp.call_tool(
                "complete_task_block",
                {
                    "user_id": user_id,
                    "block_id": completion_data.get("block_id", ""),
                    "proof_data": completion_data.get("proof_data", {})
                }
            )
            
            # Calculate points based on validation
            points = 10
            if validation_result:
                validation_output = validation_result.get("output", {})
                if validation_output.get("is_valid", False):
                    confidence = validation_output.get("confidence_score", 0.5)
                    points = int(10 * confidence)
            
            points_result = await unified_mcp.call_tool(
                "award_points",
                {
                    "user_id": user_id,
                    "points": points,
                    "reason": f"Completed task: {completion_data.get('task_title', '')}"
                }
            )
            
            # 5. PLANNER: Plan follow-up actions
            planned_actions = await action_planner.plan_task_completion(user_id, completion_data)
            
            # 6. MEMORY: Update user context and store completion insights
            completion_insights = {
                "validation": validation_result.get("output", {}) if validation_result else {},
                "motivation": motivation_result.get("output", {}),
                "points_awarded": points,
                "completion_time": datetime.now().isoformat(),
                "proof_provided": bool(completion_data.get("proof_text"))
            }
            
            await memory_manager.store_task_insights(
                user_id,
                task_id,
                {"completion": completion_insights}
            )
            
            await self._update_user_context(user_id, {
                "last_task_completed": datetime.now().isoformat(),
                "total_completions": user_context.get("total_completions", 0) + 1
            })
            
            return {
                "success": True,
                "validation": validation_result.get("output", {}) if validation_result else None,
                "motivation": motivation_result.get("output", {}),
                "points_awarded": points,
                "planned_actions": len(planned_actions),
                "completion_recorded": complete_result.get("success", False)
            }
            
        except Exception as e:
            logger.error(f"Task completion workflow failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_daily_optimization(self, user_id: str, optimization_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle daily optimization workflow
        """
        logger.info(f"Handling daily optimization for user {user_id}")
        
        try:
            # 1. MEMORY: Gather comprehensive user data
            user_context = await memory_manager.get_user_context(user_id)
            
            # Get recent chain results for pattern analysis
            recent_actions = await memory_manager.memory_store.search_memories(
                MemoryType.WORKING,
                {"key": {"$regex": "action_result:.*"}},
                user_id,
                limit=10
            )
            
            # 2. MCP: Get user dashboard and mood analysis
            dashboard_result = await unified_mcp.call_tool(
                "get_user_dashboard",
                {"user_id": user_id}
            )
            
            mood_analysis_result = await unified_mcp.call_tool(
                "mood_analysis",
                {"user_id": user_id, "days_back": 7}
            )
            
            # 3. CHAINS: Generate personalized motivation
            motivation_result = await chain_executor.execute_chain(
                "motivation",
                {
                    "mood": optimization_data.get("current_mood", "neutral"),
                    "challenge": optimization_data.get("current_challenge", ""),
                    "accomplishments": optimization_data.get("recent_accomplishments", [])
                },
                user_id
            )
            
            # 4. PLANNER: Create optimization action plan
            planned_actions = await action_planner.plan_daily_optimization(user_id, optimization_data)
            
            # 5. MEMORY: Store optimization insights
            optimization_insights = {
                "dashboard_data": dashboard_result.get("result", {}),
                "mood_patterns": mood_analysis_result.get("result", {}),
                "motivation": motivation_result.get("output", {}),
                "recent_activity": len(recent_actions),
                "optimization_date": datetime.now().date().isoformat(),
                "planned_actions": len(planned_actions)
            }
            
            await memory_manager.memory_store.store_memory(
                MemoryType.LONG_TERM,
                f"daily_optimization:{user_id}:{datetime.now().date()}",
                optimization_insights,
                user_id
            )
            
            # 6. Execute high-priority actions immediately
            executed_actions = await action_planner.execute_ready_actions(user_id, max_actions=3)
            
            return {
                "success": True,
                "dashboard": dashboard_result.get("result", {}),
                "mood_analysis": mood_analysis_result.get("result", {}),
                "motivation": motivation_result.get("output", {}),
                "planned_actions": len(planned_actions),
                "executed_actions": len(executed_actions),
                "optimization_score": self._calculate_optimization_score(optimization_insights)
            }
            
        except Exception as e:
            logger.error(f"Daily optimization workflow failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_focus_session(self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle focus session workflow with ritual recommendations
        """
        logger.info(f"Handling focus session for user {user_id}")
        
        try:
            # 1. MEMORY: Get user preferences and past session data
            user_context = await memory_manager.get_user_context(user_id)
            
            # 2. CHAINS: Get task analysis for the session
            task_analysis = None
            if session_data.get("task_id"):
                task_analysis = await chain_executor.execute_chain(
                    "task_analysis",
                    {
                        "title": session_data.get("task_title", ""),
                        "description": session_data.get("task_description", ""),
                        "duration_minutes": session_data.get("duration_minutes", 25),
                        "skill_level": user_context.get("skill_level", "intermediate")
                    },
                    user_id
                )
            
            # 3. MCP: Get ritual suggestions
            ritual_result = await unified_mcp.call_tool(
                "ritual_suggestion",
                {
                    "user_mood": session_data.get("current_mood", "neutral"),
                    "task_type": session_data.get("task_type", "general"),
                    "time_of_day": session_data.get("time_of_day", "morning"),
                    "preferences": user_context.get("ritual_preferences", {})
                }
            )
            
            # 4. MCP: Start the focus session
            session_result = await unified_mcp.call_tool(
                "start_task_block",
                {
                    "user_id": user_id,
                    "block_id": session_data.get("block_id", f"session_{datetime.now().timestamp()}")
                }
            )
            
            # 5. MCP: Play ritual playlist if suggested
            playlist_result = None
            ritual_data = ritual_result.get("result", {})
            if ritual_data.get("spotify_playlist_id"):
                playlist_result = await unified_mcp.call_tool(
                    "play_spotify_playlist",
                    {
                        "user_id": user_id,
                        "playlist_id": ritual_data["spotify_playlist_id"]
                    }
                )
            
            # 6. MEMORY: Store session context
            session_context = {
                "session_start": datetime.now().isoformat(),
                "task_analysis": task_analysis.get("output", {}) if task_analysis else {},
                "ritual_suggestion": ritual_data,
                "playlist_played": bool(playlist_result and playlist_result.get("success")),
                "session_data": session_data
            }
            
            await memory_manager.memory_store.store_memory(
                MemoryType.WORKING,
                f"focus_session:{user_id}:{datetime.now().timestamp()}",
                session_context,
                user_id
            )
            
            return {
                "success": True,
                "session_started": session_result.get("success", False),
                "ritual_suggestion": ritual_data,
                "playlist_started": bool(playlist_result and playlist_result.get("success")),
                "task_analysis": task_analysis.get("output", {}) if task_analysis else None,
                "session_context": session_context
            }
            
        except Exception as e:
            logger.error(f"Focus session workflow failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===== BACKGROUND PROCESSING =====
    
    async def _start_background_processing(self):
        """Start background processing tasks"""
        
        # Action execution task
        action_task = asyncio.create_task(self._background_action_executor())
        self.background_tasks.add(action_task)
        
        # Memory cleanup task
        cleanup_task = asyncio.create_task(self._background_memory_cleanup())
        self.background_tasks.add(cleanup_task)
        
        # Event processing task
        event_task = asyncio.create_task(self._background_event_processor())
        self.background_tasks.add(event_task)
        
        self.is_processing = True
        logger.info("Background processing tasks started")
    
    async def _background_action_executor(self):
        """Background task for executing planned actions"""
        while self.is_processing:
            try:
                # Execute ready actions for all users
                executed_actions = await action_planner.execute_ready_actions(max_actions=5)
                
                if executed_actions:
                    logger.info(f"Background executor completed {len(executed_actions)} actions")
                
                # Clean up old actions
                await action_planner.cleanup_completed_actions(older_than_hours=24)
                
                # Wait before next execution cycle
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Background action executor error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _background_memory_cleanup(self):
        """Background task for memory cleanup"""
        while self.is_processing:
            try:
                await memory_manager.cleanup_all_memories()
                logger.info("Background memory cleanup completed")
                
                # Run cleanup every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Background memory cleanup error: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _background_event_processor(self):
        """Background task for processing events"""
        while self.is_processing:
            try:
                # Process events from the queue
                while not self.processing_queue.empty():
                    event = await self.processing_queue.get()
                    await self._process_event(event)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Background event processor error: {e}")
                await asyncio.sleep(30)
    
    # ===== UTILITY METHODS =====
    
    async def _update_user_context(self, user_id: str, updates: Dict[str, Any]):
        """Update user context in memory"""
        current_context = await memory_manager.get_user_context(user_id)
        updated_context = {**current_context, **updates}
        await memory_manager.store_user_context(user_id, updated_context)
    
    def _calculate_optimization_score(self, insights: Dict[str, Any]) -> float:
        """Calculate optimization score based on insights"""
        score = 0.5  # Base score
        
        # Increase score based on activity level
        if insights.get("recent_activity", 0) > 5:
            score += 0.2
        
        # Increase score based on planned actions
        if insights.get("planned_actions", 0) > 3:
            score += 0.2
        
        # Adjust based on mood patterns
        mood_patterns = insights.get("mood_patterns", {})
        if mood_patterns.get("average_mood", 3) > 3.5:
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    async def _process_event(self, event: Dict[str, Any]):
        """Process a single event"""
        event_type = event.get("type")
        if event_type in self.event_handlers:
            handler = self.event_handlers[event_type]
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")
    
    def register_event_handler(self, event_type: str, handler):
        """Register an event handler"""
        self.event_handlers[event_type] = handler
    
    async def queue_event(self, event: Dict[str, Any]):
        """Queue an event for processing"""
        await self.processing_queue.put(event)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        memory_status = await memory_manager.memory_store.get_system_status() if hasattr(memory_manager.memory_store, 'get_system_status') else {}
        mcp_status = await unified_mcp.get_system_status()
        
        return {
            "orchestrator_initialized": self.initialized,
            "background_processing": self.is_processing,
            "background_tasks": len(self.background_tasks),
            "processing_queue_size": self.processing_queue.qsize(),
            "memory_system": memory_status,
            "mcp_system": mcp_status,
            "active_actions": len(action_planner.actions),
            "registered_event_handlers": len(self.event_handlers)
        }


# Global orchestrator instance
mcp_orchestrator = MCPOrchestrator()
