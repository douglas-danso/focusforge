"""
Custom Ritual Builder Service for FocusForge
Allows users to create personalized focus session rituals
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId

from app.core.database import get_database
from app.services.spotify_service import SpotifyService
from app.models.schemas import RitualCreate, Ritual, RitualStep, MeditationSession

logger = logging.getLogger(__name__)

class MeditationService:
    """Meditation timer and guidance service"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.meditation_sessions
    
    async def start_meditation_session(self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a guided meditation session"""
        try:
            session = {
                "user_id": user_id,
                "type": session_data.get("type", "breathing"),
                "duration_minutes": session_data.get("duration_minutes", 5),
                "guidance_voice": session_data.get("guidance_voice", "calm_female"),
                "background_sound": session_data.get("background_sound", "nature"),
                "started_at": datetime.now(),
                "completed": False,
                "completed_at": None,
                "session_notes": "",
                "mood_before": session_data.get("mood_before", ""),
                "mood_after": ""
            }
            
            result = await self.collection.insert_one(session)
            session["_id"] = str(result.inserted_id)
            
            # Generate meditation script based on type
            script = await self._generate_meditation_script(
                session["type"], 
                session["duration_minutes"]
            )
            
            return {
                "success": True,
                "session_id": session["_id"],
                "session": session,
                "meditation_script": script,
                "instructions": [
                    "Find a comfortable seated position",
                    "Close your eyes or soften your gaze",
                    "Follow the guided instructions",
                    "Don't worry if your mind wanders - that's normal"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to start meditation session: {e}")
            return {"success": False, "error": str(e)}
    
    async def complete_meditation_session(self, session_id: str, user_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a meditation session"""
        try:
            update_data = {
                "completed": True,
                "completed_at": datetime.now(),
                "mood_after": completion_data.get("mood_after", ""),
                "session_notes": completion_data.get("notes", ""),
                "effectiveness_rating": completion_data.get("rating", 5)
            }
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(session_id), "user_id": user_id},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                return {
                    "success": True,
                    "session": {
                        **result,
                        "_id": str(result["_id"])
                    },
                    "completion_message": "Great job! Meditation completed successfully."
                }
            else:
                return {"success": False, "error": "Session not found"}
        except Exception as e:
            logger.error(f"Failed to complete meditation session: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_meditation_script(self, meditation_type: str, duration_minutes: int) -> Dict[str, Any]:
        """Generate meditation script based on type and duration"""
        scripts = {
            "breathing": {
                "intro": "Welcome to your breathing meditation. Let's begin by taking three deep breaths together.",
                "main_instructions": [
                    "Breathe in slowly through your nose for 4 counts",
                    "Hold your breath gently for 4 counts", 
                    "Exhale slowly through your mouth for 6 counts",
                    "Rest for 2 counts, then repeat"
                ],
                "intervals": list(range(0, duration_minutes * 60, 30)),  # Every 30 seconds
                "closing": "Take three final deep breaths and slowly open your eyes when ready."
            },
            "body_scan": {
                "intro": "Welcome to your body scan meditation. We'll systematically relax each part of your body.",
                "main_instructions": [
                    "Start by noticing your toes, let them relax",
                    "Move your attention to your feet and ankles",
                    "Feel your calves and knees releasing tension",
                    "Notice your thighs and hips softening",
                    "Relax your lower back and abdomen",
                    "Feel your chest and shoulders dropping",
                    "Let your arms and hands become heavy",
                    "Relax your neck and facial muscles"
                ],
                "intervals": list(range(0, duration_minutes * 60, duration_minutes * 60 // 8)),
                "closing": "Notice your whole body feeling relaxed and peaceful."
            },
            "mindfulness": {
                "intro": "Welcome to mindfulness meditation. We'll practice observing the present moment.",
                "main_instructions": [
                    "Notice your breath without changing it",
                    "When thoughts arise, acknowledge them and return to breath",
                    "Observe any sounds around you without judgment",
                    "Feel the sensations in your body",
                    "Rest in this moment of awareness"
                ],
                "intervals": list(range(0, duration_minutes * 60, 60)),  # Every minute
                "closing": "Thank yourself for taking this time for mindfulness."
            },
            "focus": {
                "intro": "Welcome to your focus meditation. We'll prepare your mind for concentrated work.",
                "main_instructions": [
                    "Set a clear intention for your upcoming work",
                    "Visualize yourself working with complete focus",
                    "Feel your mind becoming sharp and clear",
                    "Breathe in energy and alertness",
                    "Exhale any distractions or worries"
                ],
                "intervals": list(range(0, duration_minutes * 60, 45)),  # Every 45 seconds
                "closing": "You are now ready to focus deeply on your work."
            }
        }
        
        return scripts.get(meditation_type, scripts["breathing"])

class RitualService:
    """Custom ritual builder and execution service"""
    
    def __init__(self, db=None):
        self.db = db
        self.collection = None
        self.executions_collection = None
        self.spotify_service = SpotifyService()
        self.meditation_service = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the ritual service"""
        if self.is_initialized:
            return
        
        if not self.db:
            self.db = await get_database()
        
        self.collection = self.db.custom_rituals
        self.executions_collection = self.db.ritual_executions
        self.meditation_service = MeditationService(self.db)
        self.is_initialized = True
        logger.info("Ritual service initialized")
    
    async def create_custom_ritual(self, user_id: str, ritual_data: RitualCreate) -> Ritual:
        """Create a custom focus ritual"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            ritual_dict = {
                "user_id": user_id,
                "name": ritual_data.name,
                "description": ritual_data.description,
                "category": ritual_data.category,
                "estimated_duration_minutes": ritual_data.estimated_duration_minutes,
                "steps": [step.dict() for step in ritual_data.steps],
                "tags": ritual_data.tags,
                "is_public": ritual_data.is_public,
                "usage_count": 0,
                "effectiveness_ratings": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_active": True
            }
            
            result = await self.collection.insert_one(ritual_dict)
            ritual_dict["_id"] = str(result.inserted_id)
            
            logger.info(f"Created custom ritual '{ritual_data.name}' for user {user_id}")
            return Ritual(**ritual_dict)
        except Exception as e:
            logger.error(f"Failed to create custom ritual: {e}")
            raise
    
    async def get_user_rituals(self, user_id: str, include_public: bool = True, category: Optional[str] = None) -> List[Ritual]:
        """Get user's custom rituals"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Build query
            query = {
                "$or": [
                    {"user_id": user_id},
                    {"is_public": True} if include_public else {}
                ],
                "is_active": True
            }
            
            if category:
                query["category"] = category
            
            cursor = self.collection.find(query).sort("created_at", -1)
            rituals = []
            
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                rituals.append(Ritual(**doc))
            
            return rituals
        except Exception as e:
            logger.error(f"Failed to get user rituals: {e}")
            return []
    
    async def get_ritual_by_id(self, ritual_id: str, user_id: str) -> Optional[Ritual]:
        """Get a specific ritual by ID"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            doc = await self.collection.find_one({
                "_id": ObjectId(ritual_id),
                "$or": [
                    {"user_id": user_id},
                    {"is_public": True}
                ]
            })
            
            if doc:
                doc["_id"] = str(doc["_id"])
                return Ritual(**doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get ritual {ritual_id}: {e}")
            return None
    
    async def execute_custom_ritual(self, user_id: str, ritual_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a custom ritual step by step"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            ritual = await self.get_ritual_by_id(ritual_id, user_id)
            if not ritual:
                return {"success": False, "error": "Ritual not found"}
            
            # Create execution record
            execution = {
                "user_id": user_id,
                "ritual_id": ritual_id,
                "ritual_name": ritual.name,
                "started_at": datetime.now(),
                "completed_at": None,
                "current_step": 0,
                "total_steps": len(ritual.steps),
                "context": context or {},
                "step_results": [],
                "completed": False,
                "effectiveness_rating": None,
                "notes": ""
            }
            
            result = await self.executions_collection.insert_one(execution)
            execution_id = str(result.inserted_id)
            
            # Execute first step
            first_step_result = await self._execute_ritual_step(
                user_id, ritual.steps[0], execution_id, 0, context
            )
            
            # Update usage count
            await self.collection.update_one(
                {"_id": ObjectId(ritual_id)},
                {"$inc": {"usage_count": 1}}
            )
            
            return {
                "success": True,
                "execution_id": execution_id,
                "ritual": {
                    "id": ritual_id,
                    "name": ritual.name,
                    "description": ritual.description,
                    "total_steps": len(ritual.steps),
                    "estimated_duration_minutes": ritual.estimated_duration_minutes
                },
                "current_step": 0,
                "step_result": first_step_result,
                "next_step_in_seconds": ritual.steps[0].duration_seconds if len(ritual.steps) > 1 else None
            }
        except Exception as e:
            logger.error(f"Failed to execute ritual: {e}")
            return {"success": False, "error": str(e)}
    
    async def advance_ritual_step(self, execution_id: str, user_id: str, step_feedback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Advance to the next step in ritual execution"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            execution = await self.executions_collection.find_one({
                "_id": ObjectId(execution_id),
                "user_id": user_id
            })
            
            if not execution:
                return {"success": False, "error": "Execution not found"}
            
            if execution["completed"]:
                return {"success": False, "error": "Ritual already completed"}
            
            # Get the ritual
            ritual = await self.get_ritual_by_id(execution["ritual_id"], user_id)
            if not ritual:
                return {"success": False, "error": "Ritual not found"}
            
            current_step_index = execution["current_step"]
            
            # Record feedback for current step
            if step_feedback:
                step_results = execution.get("step_results", [])
                if len(step_results) <= current_step_index:
                    step_results.extend([{}] * (current_step_index + 1 - len(step_results)))
                step_results[current_step_index] = step_feedback
                
                await self.executions_collection.update_one(
                    {"_id": ObjectId(execution_id)},
                    {"$set": {"step_results": step_results}}
                )
            
            next_step_index = current_step_index + 1
            
            # Check if ritual is complete
            if next_step_index >= len(ritual.steps):
                return await self._complete_ritual_execution(execution_id, user_id)
            
            # Execute next step
            next_step = ritual.steps[next_step_index]
            step_result = await self._execute_ritual_step(
                user_id, next_step, execution_id, next_step_index, execution.get("context", {})
            )
            
            # Update current step
            await self.executions_collection.update_one(
                {"_id": ObjectId(execution_id)},
                {"$set": {"current_step": next_step_index}}
            )
            
            return {
                "success": True,
                "execution_id": execution_id,
                "current_step": next_step_index,
                "total_steps": len(ritual.steps),
                "step_result": step_result,
                "is_last_step": next_step_index == len(ritual.steps) - 1,
                "progress_percentage": round((next_step_index + 1) / len(ritual.steps) * 100, 1)
            }
        except Exception as e:
            logger.error(f"Failed to advance ritual step: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_ritual_step(self, user_id: str, step: RitualStep, execution_id: str, step_index: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single ritual step"""
        try:
            step_result = {
                "step_type": step.step_type,
                "title": step.title,
                "description": step.description,
                "duration_seconds": step.duration_seconds,
                "started_at": datetime.now().isoformat()
            }
            
            if step.step_type == "spotify_playlist":
                # Play Spotify playlist
                if step.spotify_playlist_id:
                    spotify_result = await self.spotify_service.play_playlist(step.spotify_playlist_id)
                    step_result["spotify_result"] = spotify_result
                    step_result["action"] = "Playing Spotify playlist"
                elif step.spotify_search_query:
                    playlists = await self.spotify_service.search_playlists(step.spotify_search_query, limit=1)
                    if playlists:
                        spotify_result = await self.spotify_service.play_playlist(playlists[0][1])
                        step_result["spotify_result"] = spotify_result
                        step_result["action"] = f"Playing playlist: {playlists[0][0]}"
                    else:
                        step_result["action"] = "No playlist found for search query"
                
            elif step.step_type == "meditation":
                # Start meditation session
                meditation_data = {
                    "type": step.meditation_type or "breathing",
                    "duration_minutes": step.duration_seconds // 60,
                    "guidance_voice": step.meditation_voice or "calm_female",
                    "background_sound": step.meditation_background or "nature"
                }
                
                meditation_result = await self.meditation_service.start_meditation_session(user_id, meditation_data)
                step_result["meditation_session"] = meditation_result
                step_result["action"] = f"Started {meditation_data['type']} meditation for {meditation_data['duration_minutes']} minutes"
                
            elif step.step_type == "environment_setup":
                # Environment setup instructions
                step_result["setup_instructions"] = step.setup_instructions or [
                    "Clear your workspace of distractions",
                    "Adjust lighting to comfortable level",
                    "Ensure you have water nearby",
                    "Set phone to do not disturb mode"
                ]
                step_result["action"] = "Prepare your environment for focus"
                
            elif step.step_type == "breathing_exercise":
                # Breathing exercise
                exercise_type = step.breathing_pattern or "4-4-4-4"
                step_result["breathing_pattern"] = exercise_type
                step_result["instructions"] = [
                    f"Follow the {exercise_type} breathing pattern",
                    "Breathe in through your nose",
                    "Hold gently",
                    "Exhale slowly through your mouth",
                    "Pause before the next breath"
                ]
                step_result["action"] = f"Breathing exercise: {exercise_type} pattern"
                
            elif step.step_type == "intention_setting":
                # Intention setting
                step_result["prompts"] = [
                    "What do you want to accomplish in this session?",
                    "How do you want to feel during your work?",
                    "What outcome would make this session successful?",
                    "Set a clear intention for your focus time"
                ]
                step_result["action"] = "Set your intention for this session"
                
            elif step.step_type == "custom_action":
                # Custom action
                step_result["custom_instructions"] = step.custom_instructions
                step_result["action"] = step.title
                
            else:
                step_result["action"] = "Unknown step type"
            
            return step_result
        except Exception as e:
            logger.error(f"Failed to execute ritual step: {e}")
            return {
                "error": str(e),
                "step_type": step.step_type,
                "action": "Step execution failed"
            }
    
    async def _complete_ritual_execution(self, execution_id: str, user_id: str) -> Dict[str, Any]:
        """Complete a ritual execution"""
        try:
            await self.executions_collection.update_one(
                {"_id": ObjectId(execution_id)},
                {"$set": {
                    "completed": True,
                    "completed_at": datetime.now()
                }}
            )
            
            return {
                "success": True,
                "ritual_completed": True,
                "execution_id": execution_id,
                "message": "🎉 Ritual completed successfully! You're now ready for focused work.",
                "next_actions": [
                    "Start your main task",
                    "Set a timer for your work session",
                    "Eliminate any remaining distractions",
                    "Trust in your preparation and focus deeply"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to complete ritual execution: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_ritual_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pre-built ritual templates"""
        templates = [
            {
                "name": "Deep Work Preparation",
                "description": "A comprehensive ritual for intense focus sessions",
                "category": "deep_work",
                "estimated_duration_minutes": 8,
                "steps": [
                    {
                        "step_type": "environment_setup",
                        "title": "Prepare Your Space",
                        "description": "Clear distractions and optimize your environment",
                        "duration_seconds": 120,
                        "setup_instructions": [
                            "Clear your desk of unnecessary items",
                            "Close all non-essential browser tabs",
                            "Put phone in another room or drawer",
                            "Adjust lighting and temperature",
                            "Get water and healthy snacks ready"
                        ]
                    },
                    {
                        "step_type": "breathing_exercise",
                        "title": "Centering Breath Work",
                        "description": "Ground yourself with focused breathing",
                        "duration_seconds": 180,
                        "breathing_pattern": "4-7-8"
                    },
                    {
                        "step_type": "meditation", 
                        "title": "Focus Meditation",
                        "description": "Prepare your mind for concentrated work",
                        "duration_seconds": 300,
                        "meditation_type": "focus",
                        "meditation_voice": "calm_male"
                    },
                    {
                        "step_type": "spotify_playlist",
                        "title": "Focus Music",
                        "description": "Start background music for concentration",
                        "duration_seconds": 30,
                        "spotify_search_query": "deep focus instrumental"
                    },
                    {
                        "step_type": "intention_setting",
                        "title": "Set Your Intention",
                        "description": "Define what you want to accomplish",
                        "duration_seconds": 60
                    }
                ]
            },
            {
                "name": "Quick Energy Boost",
                "description": "Fast ritual to energize and refocus",
                "category": "energy",
                "estimated_duration_minutes": 3,
                "steps": [
                    {
                        "step_type": "breathing_exercise",
                        "title": "Energizing Breath",
                        "description": "Quick breathing to boost energy",
                        "duration_seconds": 90,
                        "breathing_pattern": "breath_of_fire"
                    },
                    {
                        "step_type": "spotify_playlist",
                        "title": "Upbeat Focus Music",
                        "description": "Energetic music to boost mood",
                        "duration_seconds": 30,
                        "spotify_search_query": "upbeat focus music"
                    },
                    {
                        "step_type": "intention_setting",
                        "title": "Quick Goal Setting",
                        "description": "Set a clear goal for the next 25 minutes",
                        "duration_seconds": 60
                    }
                ]
            },
            {
                "name": "Calm & Centered",
                "description": "Relaxing ritual for stressed or anxious moments",
                "category": "calm",
                "estimated_duration_minutes": 6,
                "steps": [
                    {
                        "step_type": "breathing_exercise",
                        "title": "Calming Breath",
                        "description": "Slow, deep breathing to reduce stress",
                        "duration_seconds": 180,
                        "breathing_pattern": "4-4-6-2"
                    },
                    {
                        "step_type": "meditation",
                        "title": "Body Scan",
                        "description": "Release tension from your body",
                        "duration_seconds": 240,
                        "meditation_type": "body_scan",
                        "meditation_background": "rain"
                    },
                    {
                        "step_type": "spotify_playlist",
                        "title": "Calming Sounds",
                        "description": "Peaceful background music",
                        "duration_seconds": 30,
                        "spotify_search_query": "peaceful ambient music"
                    }
                ]
            },
            {
                "name": "Creative Flow",
                "description": "Ritual to enhance creativity and inspiration",
                "category": "creative", 
                "estimated_duration_minutes": 5,
                "steps": [
                    {
                        "step_type": "environment_setup",
                        "title": "Creative Space Setup",
                        "description": "Prepare environment for creative work",
                        "duration_seconds": 60,
                        "setup_instructions": [
                            "Open curtains for natural light",
                            "Get drawing materials or notebook ready",
                            "Clear physical and digital clutter",
                            "Light a candle or incense if available"
                        ]
                    },
                    {
                        "step_type": "meditation",
                        "title": "Open Awareness",
                        "description": "Cultivate an open, receptive mindset",
                        "duration_seconds": 180,
                        "meditation_type": "mindfulness",
                        "meditation_background": "birds"
                    },
                    {
                        "step_type": "spotify_playlist",
                        "title": "Creative Inspiration",
                        "description": "Music to spark creativity",
                        "duration_seconds": 30,
                        "spotify_search_query": "creative inspiration music"
                    },
                    {
                        "step_type": "intention_setting",
                        "title": "Creative Intention",
                        "description": "Set intention for creative exploration",
                        "duration_seconds": 60
                    }
                ]
            }
        ]
        
        if category:
            templates = [t for t in templates if t["category"] == category]
        
        return templates
    
    async def create_ritual_from_template(self, user_id: str, template_name: str, customizations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a custom ritual from a template"""
        try:
            templates = await self.get_ritual_templates()
            template = next((t for t in templates if t["name"] == template_name), None)
            
            if not template:
                return {"success": False, "error": "Template not found"}
            
            # Apply customizations
            if customizations:
                template.update(customizations)
            
            # Create the ritual
            steps = [RitualStep(**step) for step in template["steps"]]
            ritual_data = RitualCreate(
                name=customizations.get("name", template["name"]),
                description=customizations.get("description", template["description"]),
                category=template["category"],
                estimated_duration_minutes=template["estimated_duration_minutes"],
                steps=steps,
                tags=customizations.get("tags", [template["category"]]),
                is_public=customizations.get("is_public", False)
            )
            
            ritual = await self.create_custom_ritual(user_id, ritual_data)
            
            return {
                "success": True,
                "ritual": ritual,
                "template_used": template_name,
                "message": f"Created ritual '{ritual.name}' from template"
            }
        except Exception as e:
            logger.error(f"Failed to create ritual from template: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_ritual_analytics(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Get analytics on ritual usage and effectiveness"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Get executions from the specified period
            start_date = datetime.now() - timedelta(days=days_back)
            
            cursor = self.executions_collection.find({
                "user_id": user_id,
                "started_at": {"$gte": start_date}
            })
            
            executions = []
            async for doc in cursor:
                executions.append(doc)
            
            # Calculate analytics
            total_rituals = len(executions)
            completed_rituals = len([e for e in executions if e.get("completed", False)])
            completion_rate = (completed_rituals / total_rituals * 100) if total_rituals > 0 else 0
            
            # Most used rituals
            ritual_usage = {}
            total_time_spent = 0
            effectiveness_ratings = []
            
            for execution in executions:
                ritual_name = execution.get("ritual_name", "Unknown")
                ritual_usage[ritual_name] = ritual_usage.get(ritual_name, 0) + 1
                
                if execution.get("completed_at") and execution.get("started_at"):
                    duration = (execution["completed_at"] - execution["started_at"]).total_seconds() / 60
                    total_time_spent += duration
                
                if execution.get("effectiveness_rating"):
                    effectiveness_ratings.append(execution["effectiveness_rating"])
            
            most_used_ritual = max(ritual_usage.items(), key=lambda x: x[1])[0] if ritual_usage else None
            avg_effectiveness = sum(effectiveness_ratings) / len(effectiveness_ratings) if effectiveness_ratings else 0
            
            return {
                "success": True,
                "period_days": days_back,
                "summary": {
                    "total_ritual_sessions": total_rituals,
                    "completed_sessions": completed_rituals,
                    "completion_rate_percent": round(completion_rate, 1),
                    "total_time_spent_minutes": round(total_time_spent, 1),
                    "avg_session_duration_minutes": round(total_time_spent / total_rituals, 1) if total_rituals > 0 else 0,
                    "most_used_ritual": most_used_ritual,
                    "avg_effectiveness_rating": round(avg_effectiveness, 1)
                },
                "ritual_usage": ritual_usage,
                "recommendations": [
                    f"Your completion rate is {round(completion_rate, 1)}% - " + (
                        "excellent consistency!" if completion_rate >= 80 else
                        "try shorter rituals to improve completion" if completion_rate < 50 else
                        "good progress, keep it up!"
                    ),
                    f"Most used ritual: {most_used_ritual}" if most_used_ritual else "Try creating more rituals",
                    f"Average effectiveness: {round(avg_effectiveness, 1)}/10" if avg_effectiveness > 0 else "Start rating your rituals for better insights"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get ritual analytics: {e}")
            return {"success": False, "error": str(e)}

# Global ritual service instance
ritual_service = RitualService()
