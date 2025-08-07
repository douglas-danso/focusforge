from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from collections import Counter
from app.models.schemas import MoodLogCreate, MoodLog

class MoodService:
    def __init__(self, db):
        self.db = db
        self.collection = db.mood_logs
    
    async def log_mood(self, user_id: str, mood_data: MoodLogCreate, 
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enhanced mood logging with context and insights"""
        # Get current mood for comparison
        current_mood = await self.get_current_mood(user_id)
        
        mood_dict = {
            "user_id": user_id,
            "feeling": mood_data.feeling,
            "intensity": getattr(mood_data, 'intensity', 5),  # 1-10 scale
            "note": mood_data.note or "",
            "context": context or {},
            "timestamp": datetime.now(),
            "triggers": getattr(mood_data, 'triggers', []),
            "related_task_id": context.get("task_id") if context else None
        }
        
        result = await self.collection.insert_one(mood_dict)
        mood_dict["_id"] = str(result.inserted_id)
        
        # Analyze mood patterns
        patterns = await self.analyze_mood_patterns(user_id)
        
        return {
            "mood_log": MoodLog(**mood_dict),
            "previous_mood": current_mood,
            "patterns": patterns,
            "insights": await self._generate_mood_insights(mood_data.feeling, current_mood, patterns)
        }
    
    async def get_current_mood(self, user_id: str) -> Optional[str]:
        """Get user's most recent mood"""
        mood_doc = await self.collection.find_one(
            {"user_id": user_id},
            sort=[("timestamp", -1)]
        )
        
        if mood_doc:
            # Consider mood "current" if logged within last 6 hours
            if (datetime.now() - mood_doc["timestamp"]).total_seconds() < 21600:
                return mood_doc.get("feeling")
        
        return None
    
    async def get_mood_for_time_period(self, user_id: str, hours_back: int = 24) -> List[str]:
        """Get moods within a specific time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        cursor = self.collection.find(
            {
                "user_id": user_id,
                "timestamp": {"$gte": cutoff_time}
            },
            {"feeling": 1, "_id": 0}
        ).sort("timestamp", -1)
        
        moods = []
        async for mood_doc in cursor:
            moods.append(mood_doc.get("feeling", ""))
        
        return moods
    
    async def analyze_mood_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze mood patterns for agent insights"""
        try:
            # Get recent mood data
            recent_moods = await self.get_mood_for_time_period(user_id, 168)  # 7 days
            trends = await self.get_mood_trends(user_id, 30)
            
            # Analyze patterns
            patterns = {
                "recent_trend": self._analyze_recent_trend(recent_moods),
                "volatility": self._calculate_mood_volatility(recent_moods),
                "dominant_mood": trends.get("most_common_mood", "neutral"),
                "average_intensity": trends.get("average_intensity", 5),
                "consistency": self._calculate_consistency(recent_moods)
            }
            
            return patterns
            
        except Exception as e:
            return {
                "recent_trend": "stable",
                "volatility": "medium",
                "dominant_mood": "neutral",
                "average_intensity": 5,
                "consistency": "medium"
            }
    
    def _analyze_recent_trend(self, recent_moods: List[str]) -> str:
        """Analyze if mood is improving, declining, or stable"""
        if len(recent_moods) < 3:
            return "insufficient_data"
        
        # Map moods to scores (higher = better)
        mood_scores = {
            "excited": 10, "happy": 8, "motivated": 9, "content": 7,
            "neutral": 5, "tired": 4, "stressed": 3, "anxious": 2,
            "sad": 1, "frustrated": 2, "overwhelmed": 2
        }
        
        scores = [mood_scores.get(mood, 5) for mood in recent_moods[:5]]
        
        if len(scores) < 3:
            return "stable"
        
        recent_avg = sum(scores[:2]) / 2
        older_avg = sum(scores[2:]) / len(scores[2:])
        
        diff = recent_avg - older_avg
        
        if diff > 1:
            return "improving"
        elif diff < -1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_mood_volatility(self, recent_moods: List[str]) -> str:
        """Calculate how much mood changes"""
        if len(recent_moods) < 2:
            return "stable"
        
        unique_moods = len(set(recent_moods[:10]))  # Look at last 10 entries
        
        if unique_moods <= 2:
            return "low"
        elif unique_moods <= 4:
            return "medium"
        else:
            return "high"
    
    def _calculate_consistency(self, recent_moods: List[str]) -> str:
        """Calculate mood consistency"""
        if len(recent_moods) < 3:
            return "unknown"
        
        # Check if mood has been consistent over recent period
        recent_sample = recent_moods[:5]
        most_common = Counter(recent_sample).most_common(1)[0]
        
        if most_common[1] / len(recent_sample) >= 0.6:
            return "high"
        elif most_common[1] / len(recent_sample) >= 0.4:
            return "medium"
        else:
            return "low"
    
    async def _generate_mood_insights(self, current_mood: str, previous_mood: Optional[str], 
                                    patterns: Dict[str, Any]) -> List[str]:
        """Generate insights about mood changes"""
        insights = []
        
        # Mood change insights
        if previous_mood and previous_mood != current_mood:
            insights.append(f"Your mood shifted from {previous_mood} to {current_mood}")
        
        # Pattern insights
        if patterns["recent_trend"] == "improving":
            insights.append("Your mood has been trending upward recently! 📈")
        elif patterns["recent_trend"] == "declining":
            insights.append("Your mood seems to be dipping. Consider taking a break or reaching out for support.")
        
        # Volatility insights
        if patterns["volatility"] == "high":
            insights.append("Your mood has been quite variable lately. Consider what might be causing these changes.")
        elif patterns["volatility"] == "low":
            insights.append("Your mood has been stable recently.")
        
        # Specific mood insights
        if current_mood in ["stressed", "anxious", "overwhelmed"]:
            insights.append("Consider trying a brief meditation or breathing exercise.")
        elif current_mood in ["excited", "motivated", "happy"]:
            insights.append("Great energy! This might be a good time to tackle challenging tasks.")
        elif current_mood == "tired":
            insights.append("You might benefit from a short break or some light activity.")
        
        return insights[:3]  # Limit to 3 insights
    
    async def get_mood_context_for_agents(self, user_id: str) -> Dict[str, Any]:
        """Get mood context specifically formatted for AI agents"""
        current_mood = await self.get_current_mood(user_id)
        patterns = await self.analyze_mood_patterns(user_id)
        recent_moods = await self.get_mood_for_time_period(user_id, 24)
        
        return {
            "current_mood": current_mood or "neutral",
            "recent_trend": patterns.get("recent_trend", "stable"),
            "volatility": patterns.get("volatility", "medium"),
            "dominant_mood": patterns.get("dominant_mood", "neutral"),
            "recent_moods_24h": recent_moods[:5],  # Last 5 moods in 24h
            "needs_support": current_mood in ["stressed", "anxious", "overwhelmed", "sad"] if current_mood else False,
            "high_energy": current_mood in ["excited", "motivated", "happy"] if current_mood else False
        }
    
    async def get_user_mood_logs(self, user_id: str, limit: int = 100, 
                                include_context: bool = False) -> List[Dict[str, Any]]:
        """Get mood logs for a user with optional context"""
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        mood_logs = []
        async for mood_doc in cursor:
            mood_doc["_id"] = str(mood_doc["_id"])
            
            if not include_context:
                # Remove context for lighter response
                mood_doc.pop("context", None)
            
            mood_logs.append(mood_doc)
        
        return mood_logs
    
    async def get_mood_trends(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Enhanced mood trends with time-based analysis"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        cursor = self.collection.find(
            {
                "user_id": user_id,
                "timestamp": {"$gte": cutoff_date}
            },
            {"feeling": 1, "intensity": 1, "timestamp": 1, "_id": 0}
        )
        
        moods = []
        intensities = []
        daily_moods = {}
        
        async for mood_doc in cursor:
            feeling = mood_doc.get("feeling", "")
            intensity = mood_doc.get("intensity", 5)
            date = mood_doc["timestamp"].date()
            
            moods.append(feeling)
            intensities.append(intensity)
            
            if date not in daily_moods:
                daily_moods[date] = []
            daily_moods[date].append(feeling)
        
        # Calculate trends
        mood_counts = dict(Counter(moods))
        avg_intensity = sum(intensities) / len(intensities) if intensities else 5
        
        # Find most common mood per day
        daily_dominant_moods = {}
        for date, day_moods in daily_moods.items():
            if day_moods:
                daily_dominant_moods[str(date)] = Counter(day_moods).most_common(1)[0][0]
        
        return {
            "period_days": days_back,
            "total_logs": len(moods),
            "mood_distribution": mood_counts,
            "average_intensity": round(avg_intensity, 2),
            "daily_dominant_moods": daily_dominant_moods,
            "most_common_mood": max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else None
        }
    
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
