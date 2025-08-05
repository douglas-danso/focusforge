from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models.schemas import PomodoroSessionCreate, PomodoroSession

class PomodoroService:
    def __init__(self, db):
        self.db = db
        self.collection = db.pomodoro_sessions
    
    async def start_session(self, user_id: str, session_data: PomodoroSessionCreate) -> PomodoroSession:
        """Start a new Pomodoro session"""
        session_dict = {
            "user_id": user_id,
            "task_id": session_data.task_id,
            "duration_minutes": session_data.duration_minutes,
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "is_completed": False
        }
        
        result = await self.collection.insert_one(session_dict)
        session_dict["_id"] = str(result.inserted_id)
        return PomodoroSession(**session_dict)
    
    async def complete_session(self, session_id: str, user_id: str) -> Optional[PomodoroSession]:
        """Complete a Pomodoro session"""
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(session_id), "user_id": user_id},
                {"$set": {
                    "completed_at": datetime.utcnow(),
                    "is_completed": True
                }},
                return_document=True
            )
            
            if result:
                result["_id"] = str(result["_id"])
                return PomodoroSession(**result)
            return None
        except Exception:
            return None
    
    async def get_user_sessions(self, user_id: str, task_id: Optional[str] = None) -> List[PomodoroSession]:
        """Get Pomodoro sessions for a user"""
        query = {"user_id": user_id}
        if task_id:
            query["task_id"] = task_id
        
        cursor = self.collection.find(query).sort("started_at", -1)
        sessions = []
        async for session_doc in cursor:
            session_doc["_id"] = str(session_doc["_id"])
            sessions.append(PomodoroSession(**session_doc))
        return sessions
    
    async def get_session(self, session_id: str, user_id: str) -> Optional[PomodoroSession]:
        """Get a specific Pomodoro session"""
        try:
            session_doc = await self.collection.find_one({
                "_id": ObjectId(session_id),
                "user_id": user_id
            })
            if session_doc:
                session_doc["_id"] = str(session_doc["_id"])
                return PomodoroSession(**session_doc)
            return None
        except Exception:
            return None
