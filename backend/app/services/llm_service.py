import json
import logging
from typing import Dict, List, Any, Optional
from app.core.enhanced_config import settings

logger = logging.getLogger(__name__)

# Constants
DEFAULT_MOTIVATION_MESSAGE = "Keep pushing forward! You've got this!"

class LLMService:
    """
    Simplified LLM service that uses the unified MCP system for AI-powered features.
    """
    
    def __init__(self):
        self.settings = settings
        logger.info("LLM Service initialized")
    
    # ===== CORE LLM METHODS =====
    
    async def decompose_task(self, task_description: str, duration_minutes: int, 
                           user_context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Decompose a task into manageable subtasks (simple version)"""
        try:
            # Use unified MCP system for task breakdown
            from app.core.unified_mcp import unified_mcp
            
            # Parse task description
            title = task_description.split(":")[0] if ":" in task_description else task_description
            description = task_description.split(":", 1)[1] if ":" in task_description else ""
            
            result = await unified_mcp.call_tool(
                "task_breakdown",
                {
                    "title": title,
                    "description": description,
                    "duration_minutes": duration_minutes,
                    "user_context": user_context or {}
                }
            )
            
            if result.get("success"):
                return result.get("breakdown", [])
            else:
                logger.warning(f"Task breakdown failed: {result.get('error')}")
                # Return fallback breakdown
                return self._create_fallback_breakdown(title, duration_minutes)
                
        except Exception as e:
            logger.error(f"Error in task decomposition: {e}")
            return self._create_fallback_breakdown(task_description, duration_minutes)
    
    def _create_fallback_breakdown(self, task_title: str, duration_minutes: int) -> List[Dict[str, Any]]:
        """Create a simple fallback breakdown when AI fails"""
        return [
            {
                "title": f"Plan: {task_title}",
                "description": "Analyze requirements and create approach",
                "estimated_minutes": max(5, duration_minutes // 4),
                "type": "planning"
            },
            {
                "title": f"Execute: {task_title}",
                "description": "Complete the main task work",
                "estimated_minutes": max(10, duration_minutes * 3 // 4),
                "type": "execution"
            },
            {
                "title": f"Review: {task_title}",
                "description": "Review and finalize the completed work",
                "estimated_minutes": max(5, duration_minutes // 6),
                "type": "review"
            }
        ]
    
    async def decompose_task_detailed(self, task_description: str, duration_minutes: int, 
                                    user_context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Decompose a task into manageable subtasks with detailed context"""
        try:
            # Use unified MCP system for task breakdown
            from app.core.unified_mcp import unified_mcp
            
            result = await unified_mcp.call_tool(
                "task_breakdown",
                {
                    "title": task_description.split(":")[0],
                    "description": task_description.split(":", 1)[1] if ":" in task_description else "",
                    "duration_minutes": duration_minutes,
                    "user_context": user_context or {}
                }
            )
            
            if result.get("success"):
                return result.get("breakdown", [])
            else:
                logger.warning(f"Task breakdown failed: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error in task decomposition: {e}")
            return []
    
    async def get_task_analysis(self, task_title: str, description: str, 
                               duration_minutes: int, user_skill_level: str = "intermediate") -> Dict[str, Any]:
        """Analyze task complexity and provide recommendations"""
        try:
            from app.core.unified_mcp import unified_mcp
            
            result = await unified_mcp.call_tool(
                "ai_task_analysis",
                {
                    "title": task_title,
                    "description": description,
                    "duration_minutes": duration_minutes,
                    "user_skill_level": user_skill_level
                }
            )
            
            if result.get("success"):
                return result.get("analysis", {})
            else:
                logger.warning(f"Task analysis failed: {result.get('error')}")
                return {}
                
        except Exception as e:
            logger.error(f"Error in task analysis: {e}")
            return {}
    
    async def get_motivational_message(self, user_context: Dict[str, Any], 
                                     current_mood: str, completed_tasks: List[Dict], 
                                     current_challenge: str = "") -> str:
        """Generate personalized motivational content"""
        try:
            from app.core.unified_mcp import unified_mcp
            
            result = await unified_mcp.call_tool(
                "ai_motivation",
                {
                    "user_context": user_context,
                    "current_mood": current_mood,
                    "challenge": current_challenge,
                    "completed_tasks": completed_tasks
                }
            )
            
            if result.get("success"):
                return result.get("motivation", DEFAULT_MOTIVATION_MESSAGE)
            else:
                logger.warning(f"Motivation generation failed: {result.get('error')}")
                return DEFAULT_MOTIVATION_MESSAGE
                
        except Exception as e:
            logger.error(f"Error generating motivation: {e}")
            return DEFAULT_MOTIVATION_MESSAGE
    
    async def validate_task_proof(self, task_description: str, proof_text: str, 
                                 completion_criteria: str = "") -> Dict[str, Any]:
        """Validate whether task proof demonstrates completion"""
        try:
            from app.core.unified_mcp import unified_mcp
            
            result = await unified_mcp.call_tool(
                "ai_proof_validation",
                {
                    "task_description": task_description,
                    "proof_text": proof_text,
                    "completion_criteria": completion_criteria
                }
            )
            
            if result.get("success"):
                return result.get("validation", {"is_valid": False, "score": 0})
            else:
                logger.warning(f"Proof validation failed: {result.get('error')}")
                return {"is_valid": False, "score": 0}
                
        except Exception as e:
            logger.error(f"Error validating proof: {e}")
            return {"is_valid": False, "score": 0}
    
    async def suggest_ritual(self, user_mood: str, task_type: str, 
                           time_of_day: str, user_preferences: Dict = None, 
                           ritual_history: List = None) -> Dict[str, Any]:
        """Suggest productivity rituals based on context"""
        try:
            from app.core.unified_mcp import unified_mcp
            
            result = await unified_mcp.call_tool(
                "ai_ritual_suggestion",
                {
                    "user_mood": user_mood,
                    "task_type": task_type,
                    "time_of_day": time_of_day,
                    "preferences": user_preferences or {},
                    "history": ritual_history or []
                }
            )
            
            if result.get("success"):
                return result.get("ritual", {})
            else:
                logger.warning(f"Ritual suggestion failed: {result.get('error')}")
                return {}
                
        except Exception as e:
            logger.error(f"Error suggesting ritual: {e}")
            return {}
    
    async def suggest_productivity_ritual(self, user_mood: str, task_type: str, 
                                        time_of_day: str = "morning", 
                                        preferences: Dict = None) -> Dict[str, Any]:
        """Suggest productivity ritual with Spotify integration"""
        try:
            # For now, return a structured fallback ritual
            # TODO: Implement LLM call when OpenAI client is properly configured
            return {
                "success": True,
                "result": self._get_fallback_ritual(user_mood, task_type)
            }
            
        except Exception as e:
            logger.error(f"Error generating productivity ritual: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": self._get_fallback_ritual(user_mood, task_type)
            }
    
    def _get_fallback_ritual(self, user_mood: str, task_type: str) -> Dict[str, Any]:
        """Generate a fallback ritual when AI fails"""
        playlist_map = {
            "coding": "37i9dQZF1DX0XUsuxWHRQd",  # Deep Focus
            "programming": "37i9dQZF1DX0XUsuxWHRQd",
            "creative": "37i9dQZF1DX4sWSpwAYIy1",  # Creative Flow
            "studying": "37i9dQZF1DX6VDO8a6cQME",  # Study Focus
            "writing": "37i9dQZF1DX3PFzdbtx1Us",  # Writing Focus
            "general": "37i9dQZF1DWZeKCadgRdKQ"   # Focus Flow
        }
        
        playlist_id = playlist_map.get(task_type.lower(), playlist_map["general"])
        
        return {
            "ritual_steps": [
                "Clear and organize your workspace",
                "Take 3 deep breaths to center yourself",
                "Set a clear intention for this session",
                "Start your focus music",
                "Begin working with full attention"
            ],
            "spotify_playlist_id": playlist_id,
            "estimated_duration_minutes": 3,
            "focus_tips": [
                "Remove all distractions from your workspace",
                "Keep water nearby to stay hydrated",
                "Use the Pomodoro technique for sustained focus"
            ],
            "environment_setup": {
                "lighting": "bright and natural",
                "temperature": "comfortable and cool",
                "distractions": "eliminated"
            },
            "breathing_exercise": {
                "technique": "Box breathing (4-4-4-4)",
                "duration_seconds": 60
            },
            "motivation": f"Ready to tackle this {task_type} session! You have everything you need to succeed."
        }
    
    async def get_comprehensive_task_guidance(self, task_data: Dict[str, Any], 
                                            user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive AI guidance for task execution"""
        try:
            from app.core.unified_mcp import unified_mcp
            
            result = await unified_mcp.call_tool(
                "task_analysis",
                {
                    "task_data": task_data,
                    "user_context": user_context
                }
            )
            
            if result.get("success"):
                return result.get("guidance", {})
            else:
                logger.warning(f"Comprehensive guidance failed: {result.get('error')}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting comprehensive guidance: {e}")
            return {}
    
    # ===== UTILITY METHODS =====
    
    def analyze_user_patterns(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user patterns to improve agent recommendations"""
        try:
            # Analyze task completion patterns
            completed_tasks = user_data.get("completed_tasks", [])
            
            patterns = {
                "preferred_task_types": self._analyze_task_preferences(completed_tasks),
                "difficulty_comfort_zone": self._analyze_difficulty_patterns(completed_tasks),
                "time_preferences": self._analyze_time_patterns(completed_tasks),
                "ritual_effectiveness": self._analyze_ritual_effectiveness(user_data.get("ritual_history", []))
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing user patterns: {e}")
            return {}
    
    def _analyze_task_preferences(self, completed_tasks: List[Dict]) -> List[str]:
        """Analyze which task types the user prefers"""
        if not completed_tasks:
            return []
        
        type_counts = {}
        for task in completed_tasks:
            task_type = task.get("type", "general")
            type_counts[task_type] = type_counts.get(task_type, 0) + 1
        
        # Sort by frequency
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return [task_type for task_type, _ in sorted_types[:3]]  # Top 3
    
    def _analyze_difficulty_patterns(self, completed_tasks: List[Dict]) -> Dict[str, Any]:
        """Analyze difficulty preferences and success rates"""
        if not completed_tasks:
            return {"preferred_difficulty": "medium", "success_rate_by_difficulty": {}}
        
        difficulty_success = {}
        for task in completed_tasks:
            difficulty = task.get("difficulty", "medium")
            success = task.get("success", False)
            
            if difficulty not in difficulty_success:
                difficulty_success[difficulty] = {"total": 0, "successful": 0}
            
            difficulty_success[difficulty]["total"] += 1
            if success:
                difficulty_success[difficulty]["successful"] += 1
        
        # Calculate success rates
        success_rates = {}
        for difficulty, stats in difficulty_success.items():
            success_rates[difficulty] = stats["successful"] / stats["total"] if stats["total"] > 0 else 0
        
        # Find preferred difficulty (highest success rate with reasonable sample size)
        preferred = max(success_rates.items(), key=lambda x: x[1]) if success_rates else ("medium", 0)
        
        return {
            "preferred_difficulty": preferred[0],
            "success_rate_by_difficulty": success_rates
        }
    
    def _analyze_time_patterns(self, completed_tasks: List[Dict]) -> Dict[str, Any]:
        """Analyze when users are most productive"""
        if not completed_tasks:
            return {"peak_hours": [], "avg_completion_time": 0}
        
        hour_completions = {}
        total_time = 0
        task_count = 0
        
        for task in completed_tasks:
            # Assuming completion_time is stored as timestamp
            completion_time = task.get("completion_time")
            if completion_time:
                hour = completion_time.hour if hasattr(completion_time, 'hour') else 12
                hour_completions[hour] = hour_completions.get(hour, 0) + 1
            
            duration = task.get("duration_minutes", 0)
            if duration > 0:
                total_time += duration
                task_count += 1
        
        # Find peak hours
        peak_hours = sorted(hour_completions.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "peak_hours": [hour for hour, _ in peak_hours],
            "avg_completion_time": total_time / task_count if task_count > 0 else 0
        }
    
    def _analyze_ritual_effectiveness(self, ritual_history: List[Dict]) -> Dict[str, Any]:
        """Analyze which rituals work best for the user"""
        if not ritual_history:
            return {"most_effective": None, "avg_rating": 0}
        
        effectiveness_by_type = {}
        for ritual in ritual_history:
            ritual_type = ritual.get("type", "unknown")
            rating = ritual.get("effectiveness_rating", 0)
            
            if ritual_type not in effectiveness_by_type:
                effectiveness_by_type[ritual_type] = []
            effectiveness_by_type[ritual_type].append(rating)
        
        # Calculate averages
        avg_by_type = {
            ritual_type: sum(ratings) / len(ratings)
            for ritual_type, ratings in effectiveness_by_type.items()
        }
        
        most_effective = max(avg_by_type.items(), key=lambda x: x[1]) if avg_by_type else None
        
        return {
            "most_effective": most_effective[0] if most_effective else None,
            "avg_rating": sum(sum(ratings) for ratings in effectiveness_by_type.values()) / sum(len(ratings) for ratings in effectiveness_by_type.values()),
            "type_effectiveness": avg_by_type
        }
