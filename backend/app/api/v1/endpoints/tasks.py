from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from app.models.schemas import TaskCreate, TaskUpdate, Task, TaskStatus
from app.services.task_service import TaskService
from app.services.llm_service import LLMService
from app.core.database import get_database

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def create_task(
    task: TaskCreate,
    auto_breakdown: bool = Query(True, description="Auto-breakdown task using AI agents"),
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Create a new task with comprehensive AI agent guidance"""
    try:
        task_service = TaskService(db)
        result = await task_service.create_task(user_id, task, auto_breakdown)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Task creation failed"))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=Dict[str, Any])
async def get_tasks(
    user_id: str = "default",  # TODO: Get from auth
    status: Optional[TaskStatus] = None,
    category: Optional[str] = None,
    include_blocks: bool = False,
    limit: int = 50,
    db=Depends(get_database)
):
    """Get all tasks for a user with filtering options"""
    try:
        task_service = TaskService(db)
        result = await task_service.get_user_tasks(
            user_id, status, category, limit, include_blocks
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard(
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get comprehensive dashboard with AI insights"""
    try:
        task_service = TaskService(db)
        dashboard = await task_service.get_user_dashboard(user_id)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_task(
    task_id: str,
    include_blocks: bool = True,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get a specific task with blocks and guidance"""
    try:
        task_service = TaskService(db)
        task = await task_service.get_task(task_id, user_id, include_blocks)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/guidance", response_model=Dict[str, Any])
async def get_task_guidance(
    task_id: str,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get comprehensive AI guidance for a specific task"""
    try:
        task_service = TaskService(db)
        guidance = await task_service.get_task_guidance(task_id, user_id)
        return guidance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/blocks/{block_id}/start", response_model=Dict[str, Any])
async def start_block(
    task_id: str,
    block_id: str,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Start working on a specific task block"""
    try:
        task_service = TaskService(db)
        result = await task_service.start_task_block(block_id, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/blocks/{block_id}/complete", response_model=Dict[str, Any])
async def complete_block(
    task_id: str,
    block_id: str,
    proof_data: Optional[Dict[str, Any]] = None,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Complete a task block with AI-powered proof validation"""
    try:
        task_service = TaskService(db)
        result = await task_service.complete_task_block(block_id, user_id, proof_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/regenerate-blocks", response_model=Dict[str, Any])
async def regenerate_blocks(
    task_id: str,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Regenerate task blocks using updated task information"""
    try:
        task_service = TaskService(db)
        result = await task_service.regenerate_task_blocks(task_id, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/motivation/support", response_model=Dict[str, Any])
async def get_motivational_support(
    challenge: str = Query("", description="Current challenge or obstacle"),
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get personalized motivational support from AI coach"""
    try:
        task_service = TaskService(db)
        support = await task_service.get_motivational_support(user_id, challenge)
        return support
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rituals/suggest", response_model=Dict[str, Any])
async def suggest_ritual(
    task_type: str = Query("general", description="Type of task to prepare for"),
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get personalized productivity ritual suggestion"""
    try:
        task_service = TaskService(db)
        ritual = await task_service.suggest_productivity_ritual(user_id, task_type)
        return ritual
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}", response_model=Dict[str, Any])
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Update a task with regeneration suggestions"""
    try:
        task_service = TaskService(db)
        updated_task = await task_service.update_task(task_id, user_id, task_update)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}", response_model=Dict[str, Any])
async def delete_task(
    task_id: str,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Delete a task and all associated blocks"""
    try:
        task_service = TaskService(db)
        result = await task_service.delete_task(task_id, user_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail="Task not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
