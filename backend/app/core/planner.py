"""
Planner layer for Memory-Chain-Planner architecture
Implements intelligent action planning and coordination
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from app.core.memory import memory_manager
from app.core.chains import chain_executor
from app.core.unified_mcp import unified_mcp
from app.core.config import settings

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Types of actions the planner can execute"""
    TASK_BREAKDOWN = "task_breakdown"
    TASK_ANALYSIS = "task_analysis"
    MOTIVATION = "motivation"
    PROOF_VALIDATION = "proof_validation"
    SCHEDULE_TASK = "schedule_task"
    START_POMODORO = "start_pomodoro"
    SEND_REMINDER = "send_reminder"
    UPDATE_MOOD = "update_mood"
    AWARD_POINTS = "award_points"
    PLAY_RITUAL = "play_ritual"
    CALENDAR_SYNC = "calendar_sync"


class ActionPriority(str, Enum):
    """Priority levels for actions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionStatus(str, Enum):
    """Status of planned actions"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PlannedAction:
    """Represents a planned action with full context"""
    action_id: str
    action_type: ActionType
    priority: ActionPriority
    user_id: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    scheduled_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    status: ActionStatus = ActionStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class ActionExecutor(ABC):
    """Base class for action executors"""
    
    @abstractmethod
    async def execute(self, action: PlannedAction) -> Dict[str, Any]:
        """Execute the action and return result"""
        pass
    
    @abstractmethod
    def can_execute(self, action: PlannedAction) -> bool:
        """Check if this executor can handle the action"""
        pass


class ChainActionExecutor(ActionExecutor):
    """Executor for chain-based actions"""
    
    def can_execute(self, action: PlannedAction) -> bool:
        return action.action_type in [
            ActionType.TASK_BREAKDOWN,
            ActionType.TASK_ANALYSIS,
            ActionType.MOTIVATION,
            ActionType.PROOF_VALIDATION
        ]
    
    async def execute(self, action: PlannedAction) -> Dict[str, Any]:
        """Execute chain-based action"""
        
        chain_mapping = {
            ActionType.TASK_BREAKDOWN: "task_breakdown",
            ActionType.TASK_ANALYSIS: "task_analysis", 
            ActionType.MOTIVATION: "motivation",
            ActionType.PROOF_VALIDATION: "proof_validation"
        }
        
        chain_name = chain_mapping[action.action_type]
        
        try:
            result = await chain_executor.execute_chain(
                chain_name, 
                action.parameters, 
                action.user_id
            )
            
            return {
                "success": True,
                "result": result.get("output", {}),
                "chain": chain_name
            }
            
        except Exception as e:
            logger.error(f"Chain execution failed for {chain_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "chain": chain_name
            }


class MCPActionExecutor(ActionExecutor):
    """Executor for MCP-based actions"""
    
    def can_execute(self, action: PlannedAction) -> bool:
        return action.action_type in [
            ActionType.SCHEDULE_TASK,
            ActionType.START_POMODORO,
            ActionType.UPDATE_MOOD,
            ActionType.AWARD_POINTS,
            ActionType.PLAY_RITUAL,
            ActionType.CALENDAR_SYNC
        ]
    
    async def execute(self, action: PlannedAction) -> Dict[str, Any]:
        """Execute MCP-based action"""
        
        mcp_tool_mapping = {
            ActionType.SCHEDULE_TASK: "create_task",
            ActionType.START_POMODORO: "start_task_block",
            ActionType.UPDATE_MOOD: "log_mood",
            ActionType.AWARD_POINTS: "award_points",
            ActionType.PLAY_RITUAL: "play_spotify_playlist",
            ActionType.CALENDAR_SYNC: "add_calendar_event"
        }
        
        tool_name = mcp_tool_mapping.get(action.action_type)
        if not tool_name:
            return {
                "success": False,
                "error": f"No MCP tool mapping for {action.action_type}"
            }
        
        try:
            # Add user_id to parameters if not present
            params = action.parameters.copy()
            if "user_id" not in params:
                params["user_id"] = action.user_id
            
            result = await unified_mcp.call_tool(tool_name, params)
            
            return {
                "success": result.get("success", False),
                "result": result.get("result", {}),
                "tool": tool_name,
                "error": result.get("error")
            }
            
        except Exception as e:
            logger.error(f"MCP execution failed for {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }


class NotificationActionExecutor(ActionExecutor):
    """Executor for notification-based actions"""
    
    def can_execute(self, action: PlannedAction) -> bool:
        return action.action_type == ActionType.SEND_REMINDER
    
    async def execute(self, action: PlannedAction) -> Dict[str, Any]:
        """Execute notification action"""
        # For now, just log the reminder
        # In production, this would send actual notifications
        
        reminder_data = action.parameters
        logger.info(f"Reminder for user {action.user_id}: {reminder_data}")
        
        return {
            "success": True,
            "result": {
                "message": "Reminder sent",
                "reminder_data": reminder_data
            }
        }


class ActionPlanner:
    """
    Intelligent action planner that decides what actions to take
    and when to execute them based on context and dependencies
    """
    
    def __init__(self):
        self.actions = {}  # action_id -> PlannedAction
        self.user_action_queues = {}  # user_id -> List[action_id]
        self.executors = [
            ChainActionExecutor(),
            MCPActionExecutor(), 
            NotificationActionExecutor()
        ]
        self.max_concurrent_actions = 5
        self.currently_executing = set()
    
    async def plan_task_creation(self, user_id: str, task_data: Dict[str, Any]) -> List[str]:
        """Plan actions for task creation workflow"""
        actions = []
        
        # 1. Analyze the task first
        analysis_action = self.create_action(
            ActionType.TASK_ANALYSIS,
            ActionPriority.HIGH,
            user_id,
            {
                "title": task_data.get("title", ""),
                "description": task_data.get("description", ""),
                "duration_minutes": task_data.get("duration_minutes", 60),
                "skill_level": task_data.get("skill_level", "intermediate")
            }
        )
        actions.append(analysis_action.action_id)
        
        # 2. Break down the task (depends on analysis)
        breakdown_action = self.create_action(
            ActionType.TASK_BREAKDOWN,
            ActionPriority.HIGH,
            user_id,
            {
                "title": task_data.get("title", ""),
                "description": task_data.get("description", ""),
                "duration_minutes": task_data.get("duration_minutes", 60)
            },
            dependencies=[analysis_action.action_id]
        )
        actions.append(breakdown_action.action_id)
        
        # 3. Schedule the task (depends on breakdown)
        schedule_action = self.create_action(
            ActionType.SCHEDULE_TASK,
            ActionPriority.MEDIUM,
            user_id,
            task_data,
            dependencies=[breakdown_action.action_id]
        )
        actions.append(schedule_action.action_id)
        
        # 4. Generate motivation if needed
        if task_data.get("needs_motivation", False):
            motivation_action = self.create_action(
                ActionType.MOTIVATION,
                ActionPriority.LOW,
                user_id,
                {
                    "mood": task_data.get("current_mood", "neutral"),
                    "challenge": f"Starting task: {task_data.get('title', '')}",
                    "accomplishments": []
                }
            )
            actions.append(motivation_action.action_id)
        
        return actions
    
    async def plan_task_completion(self, user_id: str, completion_data: Dict[str, Any]) -> List[str]:
        """Plan actions for task completion workflow"""
        actions = []
        
        # 1. Validate proof if provided
        if completion_data.get("proof_text"):
            validation_action = self.create_action(
                ActionType.PROOF_VALIDATION,
                ActionPriority.HIGH,
                user_id,
                {
                    "task_description": completion_data.get("task_description", ""),
                    "completion_criteria": completion_data.get("completion_criteria", ""),
                    "proof_text": completion_data.get("proof_text", "")
                }
            )
            actions.append(validation_action.action_id)
            
            # 2. Award points (depends on validation)
            points_action = self.create_action(
                ActionType.AWARD_POINTS,
                ActionPriority.MEDIUM,
                user_id,
                {
                    "points": completion_data.get("points", 10),
                    "reason": f"Completed task: {completion_data.get('task_title', '')}"
                },
                dependencies=[validation_action.action_id]
            )
            actions.append(points_action.action_id)
        else:
            # Award points directly if no proof validation needed
            points_action = self.create_action(
                ActionType.AWARD_POINTS,
                ActionPriority.MEDIUM,
                user_id,
                {
                    "points": completion_data.get("points", 5),
                    "reason": f"Completed task: {completion_data.get('task_title', '')}"
                }
            )
            actions.append(points_action.action_id)
        
        # 3. Generate celebration motivation
        celebration_action = self.create_action(
            ActionType.MOTIVATION,
            ActionPriority.LOW,
            user_id,
            {
                "mood": "high",
                "challenge": "",
                "accomplishments": [completion_data.get("task_title", "")]
            }
        )
        actions.append(celebration_action.action_id)
        
        return actions
    
    async def plan_daily_optimization(self, user_id: str, optimization_data: Dict[str, Any]) -> List[str]:
        """Plan actions for daily optimization"""
        actions = []
        
        # 1. Update mood tracking
        mood_action = self.create_action(
            ActionType.UPDATE_MOOD,
            ActionPriority.LOW,
            user_id,
            {
                "feeling": optimization_data.get("mood", "neutral"),
                "note": "Daily check-in",
                "context": optimization_data
            }
        )
        actions.append(mood_action.action_id)
        
        # 2. Generate motivational support
        motivation_action = self.create_action(
            ActionType.MOTIVATION,
            ActionPriority.LOW,
            user_id,
            {
                "mood": optimization_data.get("mood", "neutral"),
                "challenge": optimization_data.get("current_challenge", ""),
                "accomplishments": optimization_data.get("recent_accomplishments", [])
            }
        )
        actions.append(motivation_action.action_id)
        
        # 3. Schedule calendar sync if enabled
        if optimization_data.get("calendar_sync_enabled", False):
            calendar_action = self.create_action(
                ActionType.CALENDAR_SYNC,
                ActionPriority.LOW,
                user_id,
                {
                    "sync_type": "daily",
                    "date": datetime.now().date().isoformat()
                }
            )
            actions.append(calendar_action.action_id)
        
        return actions
    
    def create_action(self, action_type: ActionType, priority: ActionPriority,
                     user_id: str, parameters: Dict[str, Any],
                     dependencies: List[str] = None,
                     scheduled_at: Optional[datetime] = None) -> PlannedAction:
        """Create a new planned action"""
        
        action_id = f"{action_type.value}_{user_id}_{datetime.now().timestamp()}"
        
        action = PlannedAction(
            action_id=action_id,
            action_type=action_type,
            priority=priority,
            user_id=user_id,
            parameters=parameters,
            dependencies=dependencies or [],
            scheduled_at=scheduled_at
        )
        
        self.actions[action_id] = action
        
        # Add to user queue
        if user_id not in self.user_action_queues:
            self.user_action_queues[user_id] = []
        self.user_action_queues[user_id].append(action_id)
        
        logger.info(f"Created action {action_id} for user {user_id}")
        
        return action
    
    async def execute_ready_actions(self, user_id: str = None, max_actions: int = None) -> List[Dict[str, Any]]:
        """Execute all ready actions for a user or globally"""
        
        if max_actions is None:
            max_actions = self.max_concurrent_actions
        
        ready_actions = await self._get_ready_actions(user_id)
        executed_results = []
        
        # Limit concurrent executions
        actions_to_execute = ready_actions[:max_actions - len(self.currently_executing)]
        
        for action in actions_to_execute:
            if action.action_id in self.currently_executing:
                continue
            
            self.currently_executing.add(action.action_id)
            result = await self._execute_action(action)
            self.currently_executing.remove(action.action_id)
            
            executed_results.append({
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "user_id": action.user_id,
                "result": result
            })
        
        return executed_results
    
    async def _get_ready_actions(self, user_id: str = None) -> List[PlannedAction]:
        """Get actions that are ready to execute"""
        ready_actions = []
        
        actions_to_check = []
        if user_id:
            action_ids = self.user_action_queues.get(user_id, [])
            actions_to_check = [self.actions[aid] for aid in action_ids if aid in self.actions]
        else:
            actions_to_check = list(self.actions.values())
        
        for action in actions_to_check:
            if self._is_action_ready(action):
                ready_actions.append(action)
        
        # Sort by priority and creation time
        priority_order = {
            ActionPriority.CRITICAL: 0,
            ActionPriority.HIGH: 1,
            ActionPriority.MEDIUM: 2,
            ActionPriority.LOW: 3
        }
        
        ready_actions.sort(key=lambda a: (priority_order[a.priority], a.created_at))
        
        return ready_actions
    
    def _is_action_ready(self, action: PlannedAction) -> bool:
        """Check if an action is ready to execute"""
        
        # Skip if not pending
        if action.status != ActionStatus.PENDING:
            return False
        
        # Skip if max attempts reached
        if action.attempts >= action.max_attempts:
            return False
        
        # Check if scheduled time has passed
        if action.scheduled_at and action.scheduled_at > datetime.now():
            return False
        
        # Check dependencies
        for dep_id in action.dependencies:
            if dep_id not in self.actions:
                continue
            dep_action = self.actions[dep_id]
            if dep_action.status != ActionStatus.COMPLETED:
                return False
        
        return True
    
    async def _execute_action(self, action: PlannedAction) -> Dict[str, Any]:
        """Execute a single action"""
        
        start_time = datetime.now()
        action.status = ActionStatus.IN_PROGRESS
        action.attempts += 1
        action.updated_at = datetime.now()
        
        # Find appropriate executor
        executor = None
        for exec_instance in self.executors:
            if exec_instance.can_execute(action):
                executor = exec_instance
                break
        
        if not executor:
            error_msg = f"No executor found for action type {action.action_type}"
            action.status = ActionStatus.FAILED
            action.error = error_msg
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Execute the action
            result = await executor.execute(action)
            
            # Update action status
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            action.execution_time_ms = int(execution_time)
            action.result = result
            action.updated_at = datetime.now()
            
            if result.get("success", False):
                action.status = ActionStatus.COMPLETED
                logger.info(f"Action {action.action_id} completed successfully")
            else:
                action.status = ActionStatus.FAILED
                action.error = result.get("error", "Unknown error")
                logger.error(f"Action {action.action_id} failed: {action.error}")
            
            # Store result in memory for context
            await memory_manager.memory_store.store_memory(
                "working",
                f"action_result:{action.action_id}",
                asdict(action),
                action.user_id
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Action execution error: {str(e)}"
            action.status = ActionStatus.FAILED
            action.error = error_msg
            action.updated_at = datetime.now()
            logger.error(f"Action {action.action_id} execution failed: {e}")
            
            return {"success": False, "error": error_msg}
    
    def get_action_status(self, action_id: str) -> Optional[PlannedAction]:
        """Get status of a specific action"""
        return self.actions.get(action_id)
    
    def get_user_actions(self, user_id: str, status: ActionStatus = None) -> List[PlannedAction]:
        """Get all actions for a user, optionally filtered by status"""
        action_ids = self.user_action_queues.get(user_id, [])
        actions = [self.actions[aid] for aid in action_ids if aid in self.actions]
        
        if status:
            actions = [a for a in actions if a.status == status]
        
        return actions
    
    def cancel_action(self, action_id: str) -> bool:
        """Cancel a pending action"""
        if action_id not in self.actions:
            return False
        
        action = self.actions[action_id]
        if action.status == ActionStatus.PENDING:
            action.status = ActionStatus.CANCELLED
            action.updated_at = datetime.now()
            return True
        
        return False
    
    async def cleanup_completed_actions(self, older_than_hours: int = 24):
        """Clean up old completed actions"""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        actions_to_remove = []
        for action_id, action in self.actions.items():
            if (action.status in [ActionStatus.COMPLETED, ActionStatus.FAILED, ActionStatus.CANCELLED] 
                and action.updated_at < cutoff_time):
                actions_to_remove.append(action_id)
        
        for action_id in actions_to_remove:
            # Remove from actions
            action = self.actions.pop(action_id, None)
            if action:
                # Remove from user queue
                if action.user_id in self.user_action_queues:
                    try:
                        self.user_action_queues[action.user_id].remove(action_id)
                    except ValueError:
                        pass
        
        logger.info(f"Cleaned up {len(actions_to_remove)} old actions")


# Global action planner instance
action_planner = ActionPlanner()
