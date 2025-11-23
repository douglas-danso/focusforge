from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from app.models.schemas import TaskCreate, TaskUpdate, Task, TaskStatus
from app.services.store_service import StoreService
from app.services.llm_service import LLMService
from app.services.mood_service import MoodService
import logging
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, db):
        self.db = db
        self.collection = db.tasks
        self.blocks_collection = db.task_blocks
        self.proof_collection = db.task_proofs
        self.store_service = StoreService(db)
        self.llm_service = LLMService()
        self.mood_service = MoodService(db)
    
    async def create_task(self, user_id: str, task_data: TaskCreate, auto_breakdown: bool = True, 
                         user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new task with comprehensive agentic guidance"""
        try:
            # Get user context for personalized guidance
            user_context = user_context or await self._get_user_context(user_id)
            
            # Get comprehensive task guidance from all agents
            task_guidance = await self.llm_service.get_comprehensive_task_guidance(
                task_data={
                    "title": task_data.title,
                    "description": task_data.description or "",
                    "duration_minutes": task_data.duration_minutes
                },
                user_context=user_context
            )
            
            # Extract agent recommendations
            recommendations = task_guidance.get("agent_recommendations", {})
            difficulty_score = recommendations.get("difficulty_score", 1.0)
            
            # Create base task with agent insights
            task_dict = {
                "user_id": user_id,
                "title": task_data.title,
                "description": task_data.description or "",
                "status": TaskStatus.pending,
                "duration_minutes": task_data.duration_minutes,
                "break_minutes": task_data.break_minutes or 5,
                "difficulty_score": difficulty_score,
                "category": task_data.category if hasattr(task_data, 'category') else "general",
                "priority": task_data.priority if hasattr(task_data, 'priority') else "medium",
                "deadline": task_data.deadline if hasattr(task_data, 'deadline') else None,
                "estimated_blocks": recommendations.get("suggested_blocks", max(1, task_data.duration_minutes // 25)),
                "blocks_completed": 0,
                "total_tokens_earned": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "completed_at": None,
                "tags": getattr(task_data, 'tags', []),
                # Agentic enhancements
                "agent_guidance": task_guidance.get("guidance", {}),
                "procrastination_risk": recommendations.get("procrastination_risk", "medium"),
                "recommended_approach": recommendations.get("recommended_approach", "analytical"),
                "suggested_ritual_duration": recommendations.get("ritual_duration", 3)
            }
            
            result = await self.collection.insert_one(task_dict)
            task_id = str(result.inserted_id)
            task_dict["_id"] = task_id
            
            # Auto-breakdown into blocks if requested
            blocks = []
            if auto_breakdown and task_guidance.get("success", True):
                try:
                    # Use detailed breakdown from agents
                    detailed_breakdown = task_guidance.get("guidance", {}).get("breakdown", [])
                    
                    if detailed_breakdown:
                        blocks = await self._create_detailed_task_blocks(
                            task_id, 
                            user_id, 
                            detailed_breakdown,
                            difficulty_score
                        )
                    else:
                        # Fallback to simple breakdown
                        breakdown_result = await self.llm_service.decompose_task(
                            f"{task_data.title}: {task_data.description}",
                            task_data.duration_minutes,
                            user_context
                        )
                        
                        blocks = await self._create_task_blocks(
                            task_id, 
                            user_id, 
                            breakdown_result,
                            difficulty_score
                        )
                    
                    # Update task with actual block count
                    await self.collection.update_one(
                        {"_id": ObjectId(task_id)},
                        {"$set": {"estimated_blocks": len(blocks)}}
                    )
                    
                except Exception as e:
                    logger.error(f"Error in task breakdown: {e}")
                    # Create single default block
                    blocks = await self._create_task_blocks(
                        task_id, 
                        user_id, 
                        [task_data.title],
                        difficulty_score
                    )
            
            return {
                "success": True,
                "task": Task(**task_dict),
                "blocks": blocks,
                "breakdown_used": auto_breakdown and len(blocks) > 1,
                "agent_guidance": task_guidance.get("guidance", {}),
                "motivational_message": task_guidance.get("guidance", {}).get("motivation", ""),
                "suggested_ritual": task_guidance.get("guidance", {}).get("ritual", {}),
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error creating task for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_detailed_task_blocks(self, task_id: str, user_id: str, 
                                          detailed_breakdown: List[Dict[str, Any]], 
                                          difficulty_score: float) -> List[Dict[str, Any]]:
        """Create task blocks from detailed agent breakdown"""
        blocks = []
        
        for i, block_data in enumerate(detailed_breakdown):
            # Extract block information from agent response
            title = block_data.get("title", f"Block {i + 1}")
            description = block_data.get("description", title)
            estimated_minutes = block_data.get("estimated_minutes", 25)
            energy_level = block_data.get("energy_level", "medium")
            completion_criteria = block_data.get("completion_criteria", "Task completed successfully")
            
            # Calculate tokens based on difficulty and energy level
            energy_multiplier = {"low": 0.8, "medium": 1.0, "high": 1.3}.get(energy_level, 1.0)
            base_tokens = max(10, int(estimated_minutes * difficulty_score * energy_multiplier))
            
            block_dict = {
                "task_id": task_id,
                "user_id": user_id,
                "block_number": i + 1,
                "title": title,
                "description": description,
                "duration_minutes": estimated_minutes,
                "break_minutes": 5 if i < len(detailed_breakdown) - 1 else 15,
                "status": "pending",
                "estimated_tokens": base_tokens,
                "actual_tokens_earned": 0,
                "energy_level": energy_level,
                "completion_criteria": completion_criteria,
                "dependencies": block_data.get("dependencies", []),
                "started_at": None,
                "completed_at": None,
                "proof_submitted": False,
                "created_at": datetime.now()
            }
            
            result = await self.blocks_collection.insert_one(block_dict)
            block_dict["_id"] = str(result.inserted_id)
            blocks.append(block_dict)
        
        return blocks

    async def _create_task_blocks(self, task_id: str, user_id: str, block_descriptions: List[str], difficulty_score: float) -> List[Dict[str, Any]]:
        """Create individual task blocks from breakdown"""
        blocks = []
        base_tokens = max(10, int(25 * difficulty_score))  # Base tokens per 25min block
        
        for i, description in enumerate(block_descriptions):
            block_dict = {
                "task_id": task_id,
                "user_id": user_id,
                "block_number": i + 1,
                "title": description,
                "description": description,
                "duration_minutes": 25,
                "break_minutes": 5 if i < len(block_descriptions) - 1 else 15,  # Longer break after last block
                "status": "pending",
                "estimated_tokens": base_tokens,
                "actual_tokens_earned": 0,
                "energy_level": "medium",
                "completion_criteria": "Task completed successfully",
                "dependencies": [],
                "started_at": None,
                "completed_at": None,
                "proof_submitted": False,
                "created_at": datetime.now()
            }
            
            result = await self.blocks_collection.insert_one(block_dict)
            block_dict["_id"] = str(result.inserted_id)
            blocks.append(block_dict)
        
        return blocks

    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context for personalized agent guidance"""
        try:
            # Get user stats and patterns
            stats = await self._get_user_task_stats(user_id)
            
            # Get mood context
            mood_context = await self.mood_service.get_mood_context_for_agents(user_id)
            
            # Get recent tasks for context
            recent_tasks_result = await self.get_user_tasks(user_id, limit=10)
            recent_tasks = [
                {
                    "title": task.title,
                    "status": task.status,
                    "difficulty_score": getattr(task, 'difficulty_score', 1.0),
                    "category": getattr(task, 'category', 'general')
                }
                for task in recent_tasks_result.get("tasks", [])
            ]
            
            # Get user preferences from user service
            user_service = UserService(self.db)
            user_profile = await user_service.get_user(user_id)
            
            # Determine skill level from user profile or derive from completion rate
            skill_level = "intermediate"
            if user_profile:
                # Could add skill level field to user model
                if stats.get("completion_rate", 0) > 80:
                    skill_level = "advanced"
                elif stats.get("completion_rate", 0) < 50:
                    skill_level = "beginner"
            
            context = {
                "skill_level": skill_level,
                "current_mood": mood_context.get("current_mood", "neutral"),
                "mood_trend": mood_context.get("recent_trend", "stable"),
                "needs_support": mood_context.get("needs_support", False),
                "high_energy": mood_context.get("high_energy", False),
                "time_of_day": datetime.now().strftime("%H:%M"),
                "preferences": {
                    "work_style": "focused",
                    "break_preference": "short",
                    "difficulty_comfort": "medium"
                },
                "recent_tasks": recent_tasks,
                "completion_rate": stats.get("completion_rate", 0),
                "avg_difficulty": stats.get("avg_difficulty", 1.0),
                "total_completed": stats.get("completed_tasks", 0),
                "mood_volatility": mood_context.get("volatility", "medium"),
                "recent_moods": mood_context.get("recent_moods_24h", [])
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {
                "skill_level": "intermediate",
                "current_mood": "neutral",
                "mood_trend": "stable",
                "needs_support": False,
                "high_energy": False,
                "time_of_day": datetime.now().strftime("%H:%M"),
                "preferences": {},
                "recent_tasks": [],
                "completion_rate": 0,
                "avg_difficulty": 1.0,
                "total_completed": 0,
                "mood_volatility": "medium",
                "recent_moods": []
            }

    async def get_task_guidance(self, task_id: str, user_id: str) -> Dict[str, Any]:
        """Get comprehensive agentic guidance for a specific task"""
        try:
            task_result = await self.get_task(task_id, user_id, include_blocks=True)
            if not task_result:
                return {"success": False, "message": "Task not found"}
            
            task = task_result["task"]
            user_context = await self._get_user_context(user_id)
            
            # Get fresh guidance from agents
            guidance = await self.llm_service.get_comprehensive_task_guidance(
                task_data={
                    "title": task.title,
                    "description": task.description,
                    "duration_minutes": task.duration_minutes
                },
                user_context=user_context
            )
            
            return {
                "success": True,
                "task_id": task_id,
                "guidance": guidance.get("guidance", {}),
                "recommendations": guidance.get("agent_recommendations", {}),
                "updated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting task guidance for {task_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get_motivational_support(self, user_id: str, current_challenge: str = "") -> Dict[str, Any]:
        """Get motivational support from MotivationCoachAgent"""
        try:
            user_context = await self._get_user_context(user_id)
            
            message = await self.llm_service.get_motivational_message(
                user_context=user_context,
                mood=user_context.get("current_mood", "neutral"),
                task_history=user_context.get("recent_tasks", []),
                current_challenge=current_challenge
            )
            
            return {
                "success": True,
                "message": message,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting motivational support: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_message": "You're doing great! Keep going! 🌟"
            }

    async def suggest_productivity_ritual(self, user_id: str, task_type: str = "general") -> Dict[str, Any]:
        """Get personalized productivity ritual suggestion"""
        try:
            user_context = await self._get_user_context(user_id)
            
            ritual = await self.llm_service.suggest_ritual(
                user_mood=user_context.get("current_mood", "neutral"),
                task_type=task_type,
                time_of_day=user_context.get("time_of_day", "morning"),
                user_preferences=user_context.get("preferences", {}),
                past_rituals=[]  # TODO: Get from user ritual history
            )
            
            return {
                "success": True,
                "ritual": ritual,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error suggesting ritual: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_tasks(self, user_id: str, status: Optional[TaskStatus] = None, 
                           category: Optional[str] = None, limit: int = 50, 
                           include_blocks: bool = False) -> Dict[str, Any]:
        """Enhanced task retrieval with filtering and stats"""
        try:
            # Build query
            query = {"user_id": user_id}
            if status:
                query["status"] = status
            if category:
                query["category"] = category
            
            # Get tasks with pagination
            cursor = self.collection.find(query).sort("created_at", DESCENDING).limit(limit)
            tasks = []
            
            async for task_doc in cursor:
                task_doc["_id"] = str(task_doc["_id"])
                
                # Include blocks if requested
                if include_blocks:
                    blocks = await self.get_task_blocks(str(task_doc["_id"]), user_id)
                    task_doc["blocks"] = blocks
                
                tasks.append(Task(**task_doc))
            
            # Get user task statistics
            stats = await self._get_user_task_stats(user_id)
            
            return {
                "tasks": tasks,
                "count": len(tasks),
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting tasks for user {user_id}: {e}")
            return {"tasks": [], "count": 0, "error": str(e)}
    
    async def _get_user_task_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user task statistics"""
        try:
            # Aggregate stats
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "total_duration": {"$sum": "$duration_minutes"},
                    "total_tokens": {"$sum": "$total_tokens_earned"}
                }}
            ]
            
            status_stats = await self.collection.aggregate(pipeline).to_list(None)
            
            # Format stats
            stats = {
                "total_tasks": 0,
                "completed_tasks": 0,
                "pending_tasks": 0,
                "in_progress_tasks": 0,
                "total_minutes_planned": 0,
                "total_tokens_earned": 0,
                "completion_rate": 0.0,
                "avg_difficulty": 0.0
            }
            
            for stat in status_stats:
                status = stat["_id"]
                count = stat["count"]
                stats["total_tasks"] += count
                stats["total_minutes_planned"] += stat["total_duration"]
                stats["total_tokens_earned"] += stat["total_tokens"]
                
                if status == TaskStatus.completed:
                    stats["completed_tasks"] = count
                elif status == TaskStatus.pending:
                    stats["pending_tasks"] = count
                elif status == TaskStatus.in_progress:
                    stats["in_progress_tasks"] = count
            
            # Calculate completion rate
            if stats["total_tasks"] > 0:
                stats["completion_rate"] = (stats["completed_tasks"] / stats["total_tasks"]) * 100
            
            # Get average difficulty
            difficulty_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": None, "avg_difficulty": {"$avg": "$difficulty_score"}}}
            ]
            
            difficulty_result = await self.collection.aggregate(difficulty_pipeline).to_list(None)
            if difficulty_result:
                stats["avg_difficulty"] = round(difficulty_result[0]["avg_difficulty"], 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting task stats for user {user_id}: {e}")
            return {}
    
    async def get_task(self, task_id: str, user_id: str, include_blocks: bool = True) -> Optional[Dict[str, Any]]:
        """Get a specific task with optional blocks"""
        try:
            task_doc = await self.collection.find_one({
                "_id": ObjectId(task_id),
                "user_id": user_id
            })
            
            if not task_doc:
                return None
            
            task_doc["_id"] = str(task_doc["_id"])
            task = Task(**task_doc)
            
            result = {"task": task}
            
            if include_blocks:
                blocks = await self.get_task_blocks(task_id, user_id)
                result["blocks"] = blocks
                result["next_block"] = self._get_next_block(blocks)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting task {task_id} for user {user_id}: {e}")
            return None
    
    async def get_task_blocks(self, task_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all blocks for a specific task"""
        try:
            cursor = self.blocks_collection.find({
                "task_id": task_id,
                "user_id": user_id
            }).sort("block_number", ASCENDING)
            
            blocks = []
            async for block_doc in cursor:
                block_doc["_id"] = str(block_doc["_id"])
                blocks.append(block_doc)
            
            return blocks
            
        except Exception as e:
            logger.error(f"Error getting blocks for task {task_id}: {e}")
            return []
    
    def _get_next_block(self, blocks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the next pending block to work on"""
        for block in blocks:
            if block["status"] == "pending":
                return block
        return None
    
    async def start_task_block(self, block_id: str, user_id: str) -> Dict[str, Any]:
        """Start working on a specific task block"""
        try:
            result = await self.blocks_collection.find_one_and_update(
                {
                    "_id": ObjectId(block_id),
                    "user_id": user_id,
                    "status": "pending"
                },
                {
                    "$set": {
                        "status": "in_progress",
                        "started_at": datetime.now()
                    }
                },
                return_document=True
            )
            
            if not result:
                return {"success": False, "message": "Block not found or already started"}
            
            # Update parent task status
            await self.collection.update_one(
                {"_id": ObjectId(result["task_id"])},
                {"$set": {"status": TaskStatus.in_progress, "updated_at": datetime.now()}}
            )
            
            return {
                "success": True,
                "message": "Block started successfully",
                "block": {**result, "_id": str(result["_id"])},
                "suggested_break_after": result["duration_minutes"],
                "estimated_tokens": result["estimated_tokens"]
            }
            
        except Exception as e:
            logger.error(f"Error starting block {block_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def complete_task_block(self, block_id: str, user_id: str, proof_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Complete a task block with optional proof"""
        try:
            # Get the block
            block = await self.blocks_collection.find_one({
                "_id": ObjectId(block_id),
                "user_id": user_id,
                "status": "in_progress"
            })
            
            if not block:
                return {"success": False, "message": "Block not found or not in progress"}
            
            # Validate proof if provided
            proof_valid = True
            proof_score = 1.0  # Default multiplier
            
            if proof_data:
                validation_result = await self._validate_proof(block, proof_data)
                proof_valid = validation_result["valid"]
                proof_score = validation_result["confidence_score"]
                
                if not proof_valid:
                    return {
                        "success": False, 
                        "message": "Proof validation failed",
                        "details": validation_result.get("reason", "Invalid proof")
                    }
            
            # Calculate tokens earned
            base_tokens = block["estimated_tokens"]
            actual_tokens = int(base_tokens * proof_score)
            
            # Update block
            await self.blocks_collection.update_one(
                {"_id": ObjectId(block_id)},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.now(),
                        "actual_tokens_earned": actual_tokens,
                        "proof_submitted": proof_data is not None,
                        "proof_score": proof_score
                    }
                }
            )
            
            # Update parent task
            await self._update_task_progress(block["task_id"], actual_tokens)
            
            # Award currency to user
            currency_result = await self.store_service.add_currency(
                user_id=user_id,
                amount=actual_tokens,
                source="task_block_completion",
                task_id=block["task_id"],
                metadata={
                    "block_id": block_id,
                    "block_number": block["block_number"],
                    "proof_score": proof_score,
                    "difficulty_multiplier": block.get("difficulty_multiplier", 1.0)
                }
            )
            
            return {
                "success": True,
                "message": "Block completed successfully! 🎉",
                "tokens_earned": actual_tokens,
                "proof_score": proof_score,
                "currency_update": currency_result,
                "next_break_minutes": block["break_minutes"]
            }
            
        except Exception as e:
            logger.error(f"Error completing block {block_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_proof(self, block: Dict[str, Any], proof_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced proof validation using ProofVerificationAgent"""
        try:
            proof_type = proof_data.get("type", "text")
            
            if proof_type == "text":
                # Use ProofVerificationAgent for intelligent validation
                validation_result = await self.llm_service.validate_task_proof(
                    task_description=block["title"],
                    proof_text=proof_data.get("content", ""),
                    completion_criteria=block.get("completion_criteria", "Task completed successfully")
                )
                return validation_result
            
            elif proof_type == "checkbox":
                # Simple checkbox validation
                return {
                    "valid": proof_data.get("checked", False),
                    "confidence_score": 1.0,
                    "reasoning": "Checkbox confirmation",
                    "feedback": "Task marked as complete",
                    "suggestions": []
                }
            
            elif proof_type == "screenshot":
                # Accept screenshots with high confidence (could add image analysis later)
                return {
                    "valid": True,
                    "confidence_score": 0.9,
                    "reasoning": "Screenshot provided as evidence",
                    "feedback": "Visual proof accepted. Great job documenting your work!",
                    "suggestions": ["Consider adding a brief description of what the screenshot shows"]
                }
            
            elif proof_type == "file_upload":
                # Accept file uploads
                return {
                    "valid": True,
                    "confidence_score": 0.85,
                    "reasoning": "File uploaded as proof of completion",
                    "feedback": "File accepted as proof of work completion",
                    "suggestions": ["Consider adding a summary of the file contents"]
                }
            
            else:
                return {
                    "valid": False,
                    "confidence_score": 0.0,
                    "reasoning": "Unsupported proof type",
                    "feedback": "Please provide a valid proof type (text, checkbox, screenshot, or file)",
                    "suggestions": ["Use text description", "Upload a screenshot", "Check completion box"]
                }
                
        except Exception as e:
            logger.error(f"Error validating proof: {e}")
            return {
                "valid": True,  # Default to valid to avoid blocking users
                "confidence_score": 0.5,
                "reasoning": "Validation error, defaulting to valid",
                "feedback": "Proof accepted. There was an issue with validation, but your work is acknowledged.",
                "suggestions": ["Try providing more detailed proof next time"]
            }
    
    async def _update_task_progress(self, task_id: str, tokens_earned: int):
        """Update parent task progress when a block is completed"""
        try:
            # Get current task state
            task = await self.collection.find_one({"_id": ObjectId(task_id)})
            if not task:
                return
            
            # Increment progress
            new_blocks_completed = task.get("blocks_completed", 0) + 1
            new_tokens_total = task.get("total_tokens_earned", 0) + tokens_earned
            
            # Check if task is fully complete
            total_blocks = await self.blocks_collection.count_documents({
                "task_id": task_id
            })
            
            status = TaskStatus.completed if new_blocks_completed >= total_blocks else TaskStatus.in_progress
            
            update_data = {
                "blocks_completed": new_blocks_completed,
                "total_tokens_earned": new_tokens_total,
                "status": status,
                "updated_at": datetime.now()
            }
            
            if status == TaskStatus.completed:
                update_data["completed_at"] = datetime.now()
            
            await self.collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": update_data}
            )
            
        except Exception as e:
            logger.error(f"Error updating task progress for {task_id}: {e}")
    
    async def update_task(self, task_id: str, user_id: str, task_update: TaskUpdate) -> Optional[Dict[str, Any]]:
        """Enhanced task update with block regeneration option"""
        try:
            update_data = {k: v for k, v in task_update.dict(exclude_unset=True).items() if v is not None}
            update_data["updated_at"] = datetime.now()
            
            # Handle status changes
            if task_update.status == TaskStatus.completed:
                update_data["completed_at"] = datetime.now()
            elif task_update.status == TaskStatus.pending:
                update_data["completed_at"] = None
            
            # If duration changed, offer to regenerate blocks
            regenerate_blocks = False
            if "duration_minutes" in update_data:
                # Check if there are incomplete blocks
                incomplete_blocks = await self.blocks_collection.count_documents({
                    "task_id": task_id,
                    "status": {"$in": ["pending"]}
                })
                
                if incomplete_blocks > 0:
                    regenerate_blocks = True
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(task_id), "user_id": user_id},
                {"$set": update_data},
                return_document=True
            )
            
            if not result:
                return None
            
            result["_id"] = str(result["_id"])
            
            response = {
                "task": Task(**result),
                "regenerate_blocks_suggested": regenerate_blocks
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return None
    
    async def regenerate_task_blocks(self, task_id: str, user_id: str) -> Dict[str, Any]:
        """Regenerate task blocks using updated task information"""
        try:
            # Get task
            task = await self.collection.find_one({
                "_id": ObjectId(task_id),
                "user_id": user_id
            })
            
            if not task:
                return {"success": False, "message": "Task not found"}
            
            # Delete existing pending blocks
            await self.blocks_collection.delete_many({
                "task_id": task_id,
                "status": "pending"
            })
            
            # Generate new breakdown
            breakdown_result = await self.llm_service.decompose_task(
                f"{task['title']}: {task.get('description', '')}",
                task["duration_minutes"]
            )
            
            # Create new blocks
            new_blocks = await self._create_task_blocks(
                task_id,
                user_id,
                breakdown_result,
                task.get("difficulty_score", 1.0)
            )
            
            # Update task with new block count
            total_blocks = await self.blocks_collection.count_documents({"task_id": task_id})
            await self.collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {"estimated_blocks": total_blocks, "updated_at": datetime.now()}}
            )
            
            return {
                "success": True,
                "message": f"Generated {len(new_blocks)} new task blocks",
                "new_blocks": new_blocks
            }
            
        except Exception as e:
            logger.error(f"Error regenerating blocks for task {task_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_task(self, task_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a task and all associated blocks"""
        try:
            # Delete task blocks first
            blocks_result = await self.blocks_collection.delete_many({
                "task_id": task_id,
                "user_id": user_id
            })
            
            # Delete task
            task_result = await self.collection.delete_one({
                "_id": ObjectId(task_id),
                "user_id": user_id
            })
            
            if task_result.deleted_count == 0:
                return {"success": False, "message": "Task not found"}
            
            return {
                "success": True,
                "message": "Task deleted successfully",
                "blocks_deleted": blocks_result.deleted_count
            }
            
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for user"""
        try:
            # Get current active tasks and blocks
            active_tasks = await self.get_user_tasks(
                user_id, 
                status=TaskStatus.in_progress, 
                limit=5, 
                include_blocks=True
            )
            
            # Get upcoming tasks
            upcoming_tasks = await self.get_user_tasks(
                user_id,
                status=TaskStatus.pending,
                limit=5
            )
            
            # Get task statistics
            stats = await self._get_user_task_stats(user_id)
            
            # Find next recommended block
            next_block = None
            for task in active_tasks["tasks"]:
                if hasattr(task, 'blocks'):
                    next_block = self._get_next_block(task.blocks)
                    if next_block:
                        next_block["task_title"] = task.title
                        break
            
            return {
                "active_tasks": active_tasks,
                "upcoming_tasks": upcoming_tasks,
                "next_block": next_block,
                "stats": stats,
                "dashboard_timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard for user {user_id}: {e}")
            return {"error": str(e)}