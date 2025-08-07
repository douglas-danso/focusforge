from typing import List, Optional, Dict
from datetime import datetime, timedelta
from bson import ObjectId
from collections import Counter
from app.models.schemas import MoodLogCreate, MoodLog

class MoodService:
    def __init__(self, db):
        self.db = db
        self.collection = db.mood_logs
    
    async def log_mood(self, user_id: str, mood_data: MoodLogCreate) -> MoodLog:
        """Log a mood entry"""
        mood_dict = {
            "user_id": user_id,
            "feeling": mood_data.feeling,
            "note": mood_data.note or "",
            "timestamp": datetime.now()
        }
        
        result = await self.collection.insert_one(mood_dict)
        mood_dict["_id"] = str(result.inserted_id)
        return MoodLog(**mood_dict)
    
    async def get_user_mood_logs(self, user_id: str, limit: int = 100) -> List[MoodLog]:
        """Get mood logs for a user"""
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        mood_logs = []
        async for mood_doc in cursor:
            mood_doc["_id"] = str(mood_doc["_id"])
            mood_logs.append(MoodLog(**mood_doc))
        return mood_logs
    
    async def get_mood_trends(self, user_id: str) -> Dict[str, int]:
        """Get mood trends for a user"""
        cursor = self.collection.find(
            {"user_id": user_id},
            {"feeling": 1, "_id": 0}
        )
        
        feelings = []
        async for mood_doc in cursor:
            feelings.append(mood_doc.get("feeling", ""))
        
        return dict(Counter(feelings))
    
    async def reset_today_logs(self, user_id: str) -> int:
        """Reset today's mood logs"""
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        result = await self.collection.delete_many({
            "user_id": user_id,
            "timestamp": {
                "$gte": start_of_day,
                "$lte": end_of_day
            }
        })
        
        return result.deleted_count
    
    async def get_streak(self, user_id: str) -> int:
        """Get current streak of consecutive days with mood logs"""
        cursor = self.collection.find(
            {"user_id": user_id},
            {"timestamp": 1, "_id": 0}
        ).sort("timestamp", -1)
        
        dates = set()
        async for mood_doc in cursor:
            dates.add(mood_doc["timestamp"].date())
        
        if not dates:
            return 0
        
        sorted_dates = sorted(dates, reverse=True)
        today = datetime.now().date()
        
        streak = 0
        current_date = today
        
        for date in sorted_dates:
            if date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
