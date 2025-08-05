from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import TaskCreate, TaskUpdate, Task, TaskStatus
from app.services.task_service import TaskService
from app.services.llm_service import LLMService
from app.core.database import get_database

router = APIRouter()

@router.post("/", response_model=Task)
async def create_task(
    task: TaskCreate,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Create a new task and decompose it using LLM"""
    try:
        task_service = TaskService(db)
        llm_service = LLMService()
        
        # Decompose task using LLM
        blocks = await llm_service.decompose_task(task.title, task.duration_minutes)
        
        # Create task with blocks
        created_task = await task_service.create_task(user_id, task, blocks)
        return created_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Task])
async def get_tasks(
    user_id: str = "default",  # TODO: Get from auth
    status: TaskStatus = None,
    db=Depends(get_database)
):
    """Get all tasks for a user"""
    try:
        task_service = TaskService(db)
        tasks = await task_service.get_user_tasks(user_id, status)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get a specific task"""
    try:
        task_service = TaskService(db)
        task = await task_service.get_task(task_id, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Update a task"""
    try:
        task_service = TaskService(db)
        updated_task = await task_service.update_task(task_id, user_id, task_update)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Delete a task"""
    try:
        task_service = TaskService(db)
        result = await task_service.delete_task(task_id, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
