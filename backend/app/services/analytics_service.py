from typing import Dict
from datetime import datetime, timedelta
from collections import Counter
from app.models.schemas import AnalyticsResponse

class AnalyticsService:
    def __init__(self, db):
        self.db = db
        self.mood_collection = db.mood_logs
        self.pomodoro_collection = db.pomodoro_sessions
        self.task_collection = db.tasks
    
    async def get_user_analytics(self, user_id: str) -> AnalyticsResponse:
        """Get comprehensive analytics for a user"""
        total_sessions = await self.get_total_sessions(user_id)
        current_streak = await self.get_streak(user_id)
        best_streak = await self.get_best_streak(user_id)
        mood_trends = await self.get_mood_trends(user_id)
        weekly_stats = await self.get_weekly_stats(user_id)
        monthly_stats = await self.get_monthly_stats(user_id)
        
        return AnalyticsResponse(
            total_sessions=total_sessions,
            current_streak=current_streak,
            best_streak=best_streak,
            mood_trends=mood_trends,
            weekly_stats=weekly_stats,
            monthly_stats=monthly_stats
        )
    
    async def get_total_sessions(self, user_id: str) -> int:
        """Get total number of sessions"""
        return await self.mood_collection.count_documents({"user_id": user_id})
    
    async def get_streak(self, user_id: str) -> int:
        """Get current streak"""
        cursor = self.mood_collection.find(
            {"user_id": user_id},
            {"timestamp": 1, "_id": 0}
        ).sort("timestamp", -1)
        
        dates = set()
        async for mood_doc in cursor:
            dates.add(mood_doc["timestamp"].date())
        
        if not dates:
            return 0
        
        sorted_dates = sorted(dates, reverse=True)
        today = datetime.utcnow().date()
        
        streak = 0
        current_date = today
        
        for date in sorted_dates:
            if date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    async def get_best_streak(self, user_id: str) -> int:
        """Get best streak"""
        cursor = self.mood_collection.find(
            {"user_id": user_id},
            {"timestamp": 1, "_id": 0}
        ).sort("timestamp", 1)
        
        dates = set()
        async for mood_doc in cursor:
            dates.add(mood_doc["timestamp"].date())
        
        if not dates:
            return 0
        
        sorted_dates = sorted(dates)
        
        best_streak = 1
        current_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                best_streak = max(best_streak, current_streak)
            else:
                current_streak = 1
        
        return best_streak
    
    async def get_mood_trends(self, user_id: str) -> Dict[str, int]:
        """Get mood trends"""
        cursor = self.mood_collection.find(
            {"user_id": user_id},
            {"feeling": 1, "_id": 0}
        )
        
        feelings = []
        async for mood_doc in cursor:
            feelings.append(mood_doc.get("feeling", ""))
        
        return dict(Counter(feelings))
    
    async def get_weekly_stats(self, user_id: str) -> Dict[str, int]:
        """Get weekly statistics"""
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=6)
        
        cursor = self.mood_collection.find({
            "user_id": user_id,
            "timestamp": {
                "$gte": datetime.combine(week_ago, datetime.min.time()),
                "$lte": datetime.combine(today, datetime.max.time())
            }
        }, {"timestamp": 1, "_id": 0})
        
        date_counts = Counter()
        async for mood_doc in cursor:
            date_counts[mood_doc["timestamp"].date()] += 1
        
        return {
            str(week_ago + timedelta(days=i)): date_counts.get(
                week_ago + timedelta(days=i), 0
            )
            for i in range(7)
        }
    
    async def get_monthly_stats(self, user_id: str) -> Dict[str, int]:
        """Get monthly statistics"""
        today = datetime.utcnow().date()
        month_ago = today - timedelta(days=29)
        
        cursor = self.mood_collection.find({
            "user_id": user_id,
            "timestamp": {
                "$gte": datetime.combine(month_ago, datetime.min.time()),
                "$lte": datetime.combine(today, datetime.max.time())
            }
        }, {"timestamp": 1, "_id": 0})
        
        date_counts = Counter()
        async for mood_doc in cursor:
            date_counts[mood_doc["timestamp"].date()] += 1
        
        return {
            str(month_ago + timedelta(days=i)): date_counts.get(
                month_ago + timedelta(days=i), 0
            )
            for i in range(30)
        }
