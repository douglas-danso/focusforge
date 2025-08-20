"""
Memory-Chain-Planner API endpoints
Enhanced endpoints that use the complete orchestrator architecture
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.orchestrator import mcp_orchestrator
from app.core.planner import action_planner, ActionType, ActionPriority
from app.core.chains import chain_executor
from app.core.memory import memory_manager
from app.core.background_tasks import task_scheduler
from app.core.database import get_database
from app.models.api_schemas import (
    TaskCreationRequest, TaskCreationResponse,
    TaskCompletionRequest, TaskCompletionResponse,
    DailyOptimizationRequest, DailyOptimizationResponse,
    FocusSessionRequest, FocusSessionResponse,
    UserActionsResponse, ExecuteActionsResponse,
    ChainExecutionRequest, ChainExecutionResponse,
    ChainSequenceRequest, ChainSequenceResponse,
    UserContextResponse, UserContextUpdateRequest,
    TaskInsightsResponse, SimilarTasksResponse,
    BackgroundTaskStatusResponse, OrchestratorStatusResponse,
    QueueEventRequest, QueueEventResponse,
    ProcessingMode, create_error_response, validate_user_id
)
from app.core.auth import get_current_user_from_token

router = APIRouter()


# ===== ORCHESTRATOR ENDPOINTS =====

@router.post("/tasks/create-enhanced", response_model=TaskCreationResponse)
async def create_task_enhanced(
    request: TaskCreationRequest,
    user_id: str = Query(..., description="User ID"),
    background_tasks: BackgroundTasks = None,
    use_background: bool = Query(True, description="Use background processing")
) -> TaskCreationResponse:
    """
    Create task using complete Memory-Chain-Planner workflow
    Can run in foreground or background
    """
    try:
        # Validate user ID
        user_id = validate_user_id(user_id)
        
        # Convert request to dict for orchestrator
        task_data = request.dict()
        
        if use_background and task_scheduler.task_manager.is_available():
            # Schedule background processing
            job_id = task_scheduler.schedule_task_creation(user_id, task_data)
            
            return TaskCreationResponse(
                success=True,
                processing=ProcessingMode.BACKGROUND,
                user_id=user_id,
                job_id=job_id
            )
        else:
            # Process immediately
            result = await mcp_orchestrator.handle_task_creation(user_id, task_data)
            
            return TaskCreationResponse(
                success=True,
                processing=ProcessingMode.IMMEDIATE,
                user_id=user_id,
                task=result.get("task"),
                analysis=result.get("analysis"),
                breakdown=result.get("breakdown"),
                planned_actions=result.get("planned_actions", 0),
                user_context_enhanced=result.get("user_context_enhanced", False),
                similar_tasks_found=result.get("similar_tasks_found", 0)
            )
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/complete-enhanced", response_model=TaskCompletionResponse)
async def complete_task_enhanced(
    request: TaskCompletionRequest,
    user_id: str = Query(..., description="User ID"),
    use_background: bool = Query(True, description="Use background processing")
) -> TaskCompletionResponse:
    """
    Complete task using Memory-Chain-Planner workflow
    """
    try:
        # Validate user ID
        user_id = validate_user_id(user_id)
        
        # Convert request to dict for orchestrator
        completion_data = request.dict()
        
        if use_background and task_scheduler.task_manager.is_available():
            # Schedule background processing
            job_id = task_scheduler.schedule_task_completion(user_id, completion_data)
            
            return TaskCompletionResponse(
                success=True,
                processing=ProcessingMode.BACKGROUND,
                user_id=user_id,
                job_id=job_id
            )
        else:
            # Process immediately
            result = await mcp_orchestrator.handle_task_completion(user_id, completion_data)
            
            return TaskCompletionResponse(
                success=True,
                processing=ProcessingMode.IMMEDIATE,
                user_id=user_id,
                validation=result.get("validation"),
                motivation=result.get("motivation"),
                points_awarded=result.get("points_awarded", 0),
                planned_actions=result.get("planned_actions", 0),
                completion_recorded=result.get("completion_recorded", False)
            )
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily-optimization", response_model=Dict[str, Any])
async def daily_optimization(
    optimization_data: Dict[str, Any],
    user_id: str = Depends(get_current_user_from_token),
    use_background: bool = True
):
    """
    Run daily optimization using Memory-Chain-Planner
    """
    try:
        if use_background and task_scheduler.task_manager.is_available():
            # Schedule background processing
            job_id = task_scheduler.schedule_daily_optimization(user_id, optimization_data)
            
            return {
                "success": True,
                "message": "Daily optimization scheduled",
                "job_id": job_id,
                "processing": "background",
                "user_id": user_id
            }
        else:
            # Process immediately
            result = await mcp_orchestrator.handle_daily_optimization(user_id, optimization_data)
            
            return {
                "success": True,
                "message": "Daily optimization completed",
                "result": result,
                "processing": "immediate",
                "user_id": user_id
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/focus-session", response_model=FocusSessionResponse)
async def start_focus_session(
    request: FocusSessionRequest,
    user_id: str = Query(..., description="User ID")
) -> FocusSessionResponse:
    """
    Start focus session with ritual recommendations
    """
    try:
        # Validate user ID
        user_id = validate_user_id(user_id)
        
        # Convert request to dict for orchestrator
        session_data = request.dict()
        
        result = await mcp_orchestrator.handle_focus_session(user_id, session_data)
        
        return FocusSessionResponse(
            success=True,
            user_id=user_id,
            session_started=result.get("session_started", False),
            ritual_suggestion=result.get("ritual_suggestion"),
            playlist_started=result.get("playlist_started", False),
            task_analysis=result.get("task_analysis"),
            session_context=result.get("session_context")
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== PLANNER ENDPOINTS =====

@router.get("/planner/actions/{user_id}", response_model=UserActionsResponse)
async def get_user_actions(
    user_id: str = Path(..., description="User ID"),
    status: Optional[str] = Query(None, description="Filter by action status")
) -> UserActionsResponse:
    """Get all planned actions for a user"""
    try:
        # Validate user ID
        user_id = validate_user_id(user_id)
        
        from app.core.planner import ActionStatus
        
        status_filter = None
        if status:
            try:
                status_filter = ActionStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        actions = action_planner.get_user_actions(user_id, status_filter)
        
        # Convert to response format using the ActionResponse schema
        from app.models.api_schemas import ActionResponse
        serialized_actions = []
        for action in actions:
            action_response = ActionResponse(
                success=True,
                action_id=action.action_id,
                action_type=action.action_type.value,
                priority=action.priority.value,
                status=action.status.value,
                user_id=action.user_id,
                parameters=action.parameters,
                dependencies=action.dependencies,
                created_at=action.created_at,
                updated_at=action.updated_at,
                scheduled_at=action.scheduled_at,
                attempts=action.attempts,
                max_attempts=action.max_attempts,
                result=action.result,
                error=action.error,
                execution_time_ms=action.execution_time_ms
            )
            serialized_actions.append(action_response)
        
        return UserActionsResponse(
            success=True,
            user_id=user_id,
            actions=serialized_actions,
            count=len(serialized_actions),
            status_filter=status
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/planner/execute/{user_id}", response_model=Dict[str, Any])
async def execute_user_actions(
    user_id: str,
    max_actions: int = 5
):
    """Execute ready actions for a specific user"""
    try:
        executed_actions = await action_planner.execute_ready_actions(user_id, max_actions)
        
        return {
            "success": True,
            "user_id": user_id,
            "executed_actions": executed_actions,
            "count": len(executed_actions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/planner/actions/{action_id}", response_model=Dict[str, Any])
async def cancel_action(action_id: str):
    """Cancel a planned action"""
    try:
        success = action_planner.cancel_action(action_id)
        
        return {
            "success": success,
            "action_id": action_id,
            "message": "Action cancelled" if success else "Action not found or not cancellable"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/planner/actions/{action_id}/status", response_model=Dict[str, Any])
async def get_action_status(action_id: str):
    """Get status of a specific action"""
    try:
        action = action_planner.get_action_status(action_id)
        
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        
        return {
            "success": True,
            "action": {
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "priority": action.priority.value,
                "status": action.status.value,
                "user_id": action.user_id,
                "created_at": action.created_at.isoformat(),
                "updated_at": action.updated_at.isoformat(),
                "attempts": action.attempts,
                "result": action.result,
                "error": action.error
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== CHAIN ENDPOINTS =====

@router.post("/chains/execute/{chain_name}", response_model=Dict[str, Any])
async def execute_chain(
    chain_name: str,
    chain_input: Dict[str, Any],
    user_id: str = Depends(get_current_user_from_token),
    use_cache: bool = True
):
    """Execute a specific chain directly"""
    try:
        result = await chain_executor.execute_chain(
            chain_name, 
            chain_input, 
            user_id, 
            use_cache
        )
        
        return {
            "success": True,
            "chain": chain_name,
            "user_id": user_id,
            "result": result,
            "cached": False  # TODO: Detect if result was cached
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chains/sequence", response_model=Dict[str, Any])
async def execute_chain_sequence(
    chain_specs: List[Dict[str, Any]],
    user_id: str = "default"
):
    """Execute a sequence of chains"""
    try:
        results = await chain_executor.execute_chain_sequence(chain_specs, user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "chain_count": len(chain_specs),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chains/cache", response_model=Dict[str, Any])
async def clear_chain_cache(
    chain_name: Optional[str] = None,
    user_id: Optional[str] = None
):
    """Clear chain cache"""
    try:
        chain_executor.clear_cache(chain_name, user_id)
        
        cache_cleared = "all caches"
        if chain_name and user_id:
            cache_cleared = f"cache for {chain_name} and user {user_id}"
        elif chain_name:
            cache_cleared = f"cache for {chain_name}"
        elif user_id:
            cache_cleared = f"cache for user {user_id}"
        
        return {
            "success": True,
            "message": f"Cleared {cache_cleared}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== MEMORY ENDPOINTS =====

@router.get("/memory/user-context/{user_id}", response_model=Dict[str, Any])
async def get_user_context(user_id: str):
    """Get user context from memory"""
    try:
        context = await memory_manager.get_user_context(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "context": context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/user-context/{user_id}", response_model=Dict[str, Any])
async def update_user_context(
    user_id: str,
    context_updates: Dict[str, Any]
):
    """Update user context in memory"""
    try:
        current_context = await memory_manager.get_user_context(user_id)
        updated_context = {**current_context, **context_updates}
        
        await memory_manager.store_user_context(user_id, updated_context)
        
        return {
            "success": True,
            "user_id": user_id,
            "updated_context": updated_context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/task-insights/{user_id}/{task_id}", response_model=Dict[str, Any])
async def get_task_insights(user_id: str, task_id: str):
    """Get task insights from memory"""
    try:
        insights = await memory_manager.get_task_insights(user_id, task_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "task_id": task_id,
            "insights": insights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/similar-tasks/{user_id}", response_model=Dict[str, Any])
async def search_similar_tasks(
    user_id: str,
    description: str,
    limit: int = 5
):
    """Search for similar tasks in memory"""
    try:
        similar_tasks = await memory_manager.search_similar_tasks(user_id, description, limit)
        
        return {
            "success": True,
            "user_id": user_id,
            "query": description,
            "similar_tasks": similar_tasks,
            "count": len(similar_tasks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memory/cleanup", response_model=Dict[str, Any])
async def cleanup_memory():
    """Run memory cleanup"""
    try:
        await memory_manager.cleanup_all_memories()
        
        return {
            "success": True,
            "message": "Memory cleanup completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== BACKGROUND TASK ENDPOINTS =====

@router.get("/background-tasks/status/{job_id}", response_model=Dict[str, Any])
async def get_background_task_status(job_id: str):
    """Get status of a background task"""
    try:
        status = task_scheduler.get_task_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "success": True,
            "job_id": job_id,
            "status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/background-tasks/{job_id}", response_model=Dict[str, Any])
async def cancel_background_task(job_id: str):
    """Cancel a background task"""
    try:
        success = task_scheduler.cancel_task(job_id)
        
        return {
            "success": success,
            "job_id": job_id,
            "message": "Task cancelled" if success else "Task not found or not cancellable"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/background-tasks/schedule-actions/{user_id}", response_model=Dict[str, Any])
async def schedule_action_execution(
    user_id: str,
    delay_seconds: int = 0
):
    """Schedule execution of user actions"""
    try:
        job_id = task_scheduler.schedule_action_execution(user_id, delay_seconds)
        
        return {
            "success": True,
            "user_id": user_id,
            "job_id": job_id,
            "delay_seconds": delay_seconds
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ORCHESTRATOR STATUS =====

@router.get("/orchestrator/status", response_model=OrchestratorStatusResponse)
async def get_orchestrator_status() -> OrchestratorStatusResponse:
    """Get detailed orchestrator status"""
    try:
        status = await mcp_orchestrator.get_system_status()
        
        return OrchestratorStatusResponse(
            success=True,
            status=status,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orchestrator/queue-event", response_model=Dict[str, Any])
async def queue_orchestrator_event(event_data: Dict[str, Any]):
    """Queue an event for orchestrator processing"""
    try:
        await mcp_orchestrator.queue_event(event_data)
        
        return {
            "success": True,
            "message": "Event queued for processing",
            "event_type": event_data.get("type", "unknown")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
