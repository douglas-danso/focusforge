from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models.schemas import TaskCreate, TaskUpdate, Task, TaskStatus

class TaskService:
    def __init__(self, db):
        self.db = db
        self.collection = db.tasks
    
    async def create_task(self, user_id: str, task_data: TaskCreate, blocks: List[str] = None) -> Task:
        """Create a new task"""
        task_dict = {
            "user_id": user_id,
            "title": task_data.title,
            "description": task_data.description,
            "status": TaskStatus.pending,
            "duration_minutes": task_data.duration_minutes,
            "break_minutes": task_data.break_minutes,
            "blocks": blocks or [],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "completed_at": None
        }
        
        result = await self.collection.insert_one(task_dict)
        task_dict["_id"] = str(result.inserted_id)
        return Task(**task_dict)
    
    async def get_user_tasks(self, user_id: str, status: Optional[TaskStatus] = None) -> List[Task]:
        """Get all tasks for a user, optionally filtered by status"""
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query).sort("created_at", -1)
        tasks = []
        async for task_doc in cursor:
            task_doc["_id"] = str(task_doc["_id"])
            tasks.append(Task(**task_doc))
        return tasks
    
    async def get_task(self, task_id: str, user_id: str) -> Optional[Task]:
        """Get a specific task"""
        try:
            task_doc = await self.collection.find_one({
                "_id": ObjectId(task_id),
                "user_id": user_id
            })
            if task_doc:
                task_doc["_id"] = str(task_doc["_id"])
                return Task(**task_doc)
            return None
        except Exception:
            return None
    
    async def update_task(self, task_id: str, user_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """Update a task"""
        try:
            update_data = {k: v for k, v in task_update.dict(exclude_unset=True).items() if v is not None}
            update_data["updated_at"] = datetime.now()
            
            if task_update.status == TaskStatus.completed:
                update_data["completed_at"] = datetime.now()
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(task_id), "user_id": user_id},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                result["_id"] = str(result["_id"])
                return Task(**result)
            return None
        except Exception:
            return None
    
    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a task"""
        try:
            result = await self.collection.delete_one({
                "_id": ObjectId(task_id),
                "user_id": user_id
            })
            return result.deleted_count > 0
        except Exception:
            return False
