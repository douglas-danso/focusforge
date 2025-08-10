from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.mcp.client import mcp_client, MCPSession
import json
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """
    Enhanced LLM Service implementing Agentic Architecture for FocusForge
    
    Agents:
    - TaskBreakdownAgent: Decomposes tasks into manageable blocks
    - MotivationCoachAgent: Provides motivational guidance and nudges
    - TaskWeightingAgent: Estimates task difficulty and complexity
    - ProofVerificationAgent: Validates task completion proofs
    - RitualAdvisorAgent: Recommends personalized productivity rituals
    
    Now enhanced with MCP (Model Context Protocol) integration for better
    context management and standardized tool access.
    """
    
    def __init__(self, use_mcp: bool = True):
        """Initialize LLM service with optional MCP integration"""
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE
        )
        
        # MCP integration toggle
        self.use_mcp = use_mcp
        
        # Simple conversation history storage (in production, would use proper memory management)
        self.conversation_history = {
            "task_breakdown": [],
            "motivation_coach": [],
            "task_weighting": [],
            "proof_verification": [],
            "ritual_advisor": []
        }
        
        self._initialize_prompts()
    
    def _initialize_prompts(self):
        """Initialize prompt templates for each agent"""
        
        # Task Breakdown Agent
        self.task_breakdown_template = PromptTemplate(
            input_variables=["task", "duration", "context", "user_preferences"],
            template="""You are a TaskBreakdownAgent, an expert at decomposing complex tasks into manageable 25-minute Pomodoro blocks.

TASK: {task}
TOTAL DURATION: {duration} minutes
CONTEXT: {context}
USER PREFERENCES: {user_preferences}

Your goal is to break this task into focused, actionable blocks that:
1. Are realistic for 25-minute sessions
2. Build momentum and maintain flow
3. Consider the user's energy levels throughout the day
4. Have clear completion criteria

Format your response as a JSON array with this structure:
[
  {{
    "block_number": 1,
    "title": "Brief, actionable title",
    "description": "Specific actions to take",
    "estimated_minutes": 25,
    "completion_criteria": "How to know this block is done",
    "energy_level": "high|medium|low",
    "dependencies": []
  }}
]

Be creative but practical. Consider cognitive load and task switching costs."""
        )
        
        # Motivation Coach Agent
        self.motivation_coach_template = PromptTemplate(
            input_variables=["user_context", "mood", "task_history", "current_challenge"],
            template="""You are a MotivationCoachAgent, a supportive AI companion helping users with ADHD, procrastination, and motivation challenges.

USER CONTEXT: {user_context}
CURRENT MOOD: {mood}
TASK HISTORY: {task_history}
CURRENT CHALLENGE: {current_challenge}

Your role is to:
1. Provide empathetic, personalized motivation
2. Acknowledge struggles without judgment
3. Suggest specific, actionable strategies
4. Use gamification elements naturally
5. Match your tone to the user's emotional state

Respond with a motivational message that includes:
- Acknowledgment of their current situation
- Specific encouragement based on their progress
- One concrete next step
- A reminder of their capabilities

Keep it under 100 words but make it genuinely helpful. Be a supportive friend, not a corporate cheerleader."""
        )
        
        # Task Weighting Agent
        self.task_weighting_template = PromptTemplate(
            input_variables=["task_title", "description", "duration", "user_skill_level"],
            template="""You are a TaskWeightingAgent that estimates task difficulty for reward calculation.

TASK: {task_title}
DESCRIPTION: {description}
DURATION: {duration} minutes
USER SKILL LEVEL: {user_skill_level}

Analyze this task across these dimensions:
1. Cognitive Complexity (how much mental effort required)
2. Learning Curve (new skills vs familiar work)
3. Focus Requirements (sustained attention needed)
4. Emotional Difficulty (motivation/procrastination factors)
5. External Dependencies (waiting on others, resources)

Return a JSON object:
{{
  "difficulty_score": 0.5-3.0,
  "reasoning": "Brief explanation of scoring",
  "complexity_factors": ["factor1", "factor2"],
  "recommended_breaks": 2,
  "energy_type": "creative|analytical|administrative|physical",
  "procrastination_risk": "low|medium|high",
  "motivation_tips": ["tip1", "tip2"]
}}

Difficulty scoring:
- 0.5-0.8: Routine, familiar tasks
- 0.9-1.2: Standard complexity
- 1.3-1.7: Challenging but manageable
- 1.8-2.5: High complexity/learning
- 2.6-3.0: Expert-level or extremely demanding"""
        )
        
        # Proof Verification Agent
        self.proof_verification_template = PromptTemplate(
            input_variables=["task_description", "proof_text", "completion_criteria"],
            template="""You are a ProofVerificationAgent that validates task completion evidence.

TASK: {task_description}
COMPLETION CRITERIA: {completion_criteria}
USER PROOF: {proof_text}

Evaluate whether the provided proof demonstrates genuine task completion:

1. Does the proof match the task requirements?
2. Is there evidence of actual work/progress?
3. Does it meet the completion criteria?
4. Are there any red flags (copy-paste, vague responses)?

Return a JSON object:
{{
  "valid": true/false,
  "confidence_score": 0.0-1.0,
  "reasoning": "Why you made this decision",
  "feedback": "Constructive feedback for the user",
  "suggestions": ["How to improve proof quality"]
}}

Be fair but thorough. The goal is to ensure users are genuinely completing tasks while being supportive of their efforts."""
        )
        
        # Ritual Advisor Agent
        self.ritual_advisor_template = PromptTemplate(
            input_variables=["user_mood", "task_type", "time_of_day", "user_preferences", "past_rituals"],
            template="""You are a RitualAdvisorAgent that creates personalized productivity rituals for users.

USER MOOD: {user_mood}
TASK TYPE: {task_type}
TIME OF DAY: {time_of_day}
USER PREFERENCES: {user_preferences}
PAST SUCCESSFUL RITUALS: {past_rituals}

Design a 3-5 minute startup ritual that will help the user enter a focused state:

Consider:
- Sensory elements (music, lighting, scents)
- Physical preparation (posture, breathing, stretching)
- Mental preparation (intention setting, visualization)
- Environmental setup (workspace, tools, distractions)
- Spotify integration if user prefers music

Return a JSON object:
{{
  "ritual_name": "Catchy name for this ritual",
  "duration_minutes": 3-5,
  "steps": [
    {{
      "action": "Specific instruction",
      "duration_seconds": 30-60,
      "type": "physical|mental|environmental|audio"
    }}
  ],
  "spotify_suggestion": {{
    "playlist_mood": "focus|energetic|calm",
    "duration": "during_ritual|during_work|both"
  }},
  "why_this_works": "Brief explanation of the science/psychology",
  "variations": ["Alternative if this doesn't work"]
}}

Make it practical, science-based, and personally relevant to their situation."""
        )
    
    # ===== TASK BREAKDOWN AGENT =====
    async def decompose_task(self, task_description: str, duration_minutes: int, 
                           user_context: Optional[Dict] = None) -> List[str]:
        """Enhanced task decomposition using TaskBreakdownAgent"""
        try:
            context = user_context or {}
            user_preferences = context.get("preferences", "No specific preferences")
            user_context_str = context.get("context", "No additional context")
            
            prompt = self.task_breakdown_template.format(
                task=task_description,
                duration=duration_minutes,
                context=user_context_str,
                user_preferences=user_preferences
            )
            
            # Add to conversation history
            self.conversation_history["task_breakdown"].append({
                "timestamp": datetime.now(),
                "prompt": task_description,
                "duration": duration_minutes
            })
            
            response = await self.llm.apredict(prompt)
            
            # Parse JSON response
            try:
                blocks_data = json.loads(response)
                # Extract just the titles for backward compatibility
                return [block["title"] for block in blocks_data]
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from task breakdown, falling back to text parsing")
                # Fallback to simple text parsing
                blocks = [block.strip() for block in response.split("\n") if block.strip()]
                return blocks or [f"Work on: {task_description}"]
            
        except Exception as e:
            logger.error(f"Error in task decomposition: {e}")
            return [f"Work on: {task_description}"]
    
    async def decompose_task_detailed(self, task_description: str, duration_minutes: int,
                                    user_context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Get detailed task breakdown with full block information"""
        try:
            context = user_context or {}
            user_preferences = context.get("preferences", "No specific preferences")
            user_context_str = context.get("context", "No additional context")
            
            prompt = self.task_breakdown_template.format(
                task=task_description,
                duration=duration_minutes,
                context=user_context_str,
                user_preferences=user_preferences
            )
            
            response = await self.llm.apredict(prompt)
            
            # Parse JSON response
            blocks_data = json.loads(response)
            return blocks_data
            
        except Exception as e:
            logger.error(f"Error in detailed task decomposition: {e}")
            # Return fallback structure
            return [{
                "block_number": 1,
                "title": f"Work on: {task_description}",
                "description": task_description,
                "estimated_minutes": duration_minutes,
                "completion_criteria": "Task is completed to satisfaction",
                "energy_level": "medium",
                "dependencies": []
            }]
    
    # ===== TASK WEIGHTING AGENT =====
    async def estimate_task_difficulty(self, task_title: str, description: str, 
                                     duration_minutes: int, user_skill_level: str = "intermediate") -> float:
        """Enhanced task difficulty estimation using TaskWeightingAgent"""
        try:
            prompt = self.task_weighting_template.format(
                task_title=task_title,
                description=description or "No description provided",
                duration=duration_minutes,
                user_skill_level=user_skill_level
            )
            
            # Add to conversation history
            self.conversation_history["task_weighting"].append({
                "timestamp": datetime.now(),
                "task": task_title,
                "duration": duration_minutes
            })
            
            response = await self.llm.apredict(prompt)
            
            # Parse JSON response
            analysis = json.loads(response)
            return analysis.get("difficulty_score", 1.0)
            
        except Exception as e:
            logger.error(f"Error in task difficulty estimation: {e}")
            # Fallback: simple duration-based estimation
            return min(max(duration_minutes / 60, 0.5), 3.0)
    
    async def get_task_analysis(self, task_title: str, description: str, 
                              duration_minutes: int, user_skill_level: str = "intermediate") -> Dict[str, Any]:
        """Get complete task analysis from TaskWeightingAgent"""
        try:
            prompt = self.task_weighting_template.format(
                task_title=task_title,
                description=description or "No description provided",
                duration=duration_minutes,
                user_skill_level=user_skill_level
            )
            
            response = await self.llm.apredict(prompt)
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error in task analysis: {e}")
            return {
                "difficulty_score": 1.0,
                "reasoning": "Default analysis due to processing error",
                "complexity_factors": ["unknown"],
                "recommended_breaks": max(1, duration_minutes // 25),
                "energy_type": "analytical",
                "procrastination_risk": "medium",
                "motivation_tips": ["Break task into smaller parts", "Set a timer for focused work"]
            }
    
    # ===== MOTIVATION COACH AGENT =====
    async def get_motivational_message(self, user_context: Dict[str, Any], 
                                     mood: str, task_history: List[Dict] = None,
                                     current_challenge: str = "") -> str:
        """Get personalized motivation from MotivationCoachAgent"""
        try:
            task_history = task_history or []
            
            # Format task history for context
            history_summary = self._format_task_history(task_history)
            
            prompt = self.motivation_coach_template.format(
                user_context=json.dumps(user_context),
                mood=mood,
                task_history=history_summary,
                current_challenge=current_challenge
            )
            
            # Add to conversation history
            self.conversation_history["motivation_coach"].append({
                "timestamp": datetime.now(),
                "mood": mood,
                "challenge": current_challenge
            })
            
            response = await self.llm.apredict(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error getting motivational message: {e}")
            return "You've got this! Every small step forward is progress. 🌟"
    
    def _format_task_history(self, task_history: List[Dict]) -> str:
        """Format task history for agent context"""
        if not task_history:
            return "No recent task history available"
        
        summary = []
        for task in task_history[-5:]:  # Last 5 tasks
            status = task.get("status", "unknown")
            title = task.get("title", "Unknown task")
            summary.append(f"- {title}: {status}")
        
        return "\n".join(summary)
    
    # ===== PROOF VERIFICATION AGENT =====
    async def validate_task_proof(self, task_description: str, proof_text: str, 
                                completion_criteria: str = "") -> Dict[str, Any]:
        """Validate task completion proof using ProofVerificationAgent"""
        try:
            prompt = self.proof_verification_template.format(
                task_description=task_description,
                proof_text=proof_text,
                completion_criteria=completion_criteria or "Task completed satisfactorily"
            )
            
            # Add to conversation history
            self.conversation_history["proof_verification"].append({
                "timestamp": datetime.now(),
                "task": task_description,
                "proof_length": len(proof_text)
            })
            
            response = await self.llm.apredict(prompt)
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error in proof validation: {e}")
            # Default to accepting proof with lower confidence
            return {
                "valid": True,
                "confidence_score": 0.7,
                "reasoning": "Unable to fully validate due to processing error, accepting proof",
                "feedback": "Proof accepted. Consider providing more specific details next time.",
                "suggestions": ["Include specific accomplishments", "Mention any challenges overcome"]
            }
    
    # ===== RITUAL ADVISOR AGENT =====
    async def suggest_ritual(self, user_mood: str, task_type: str, 
                           time_of_day: str, user_preferences: Dict = None,
                           past_rituals: List[Dict] = None) -> Dict[str, Any]:
        """Get personalized ritual suggestion from RitualAdvisorAgent"""
        try:
            user_preferences = user_preferences or {}
            past_rituals = past_rituals or []
            
            # Format past rituals
            past_rituals_summary = self._format_past_rituals(past_rituals)
            
            prompt = self.ritual_advisor_template.format(
                user_mood=user_mood,
                task_type=task_type,
                time_of_day=time_of_day,
                user_preferences=json.dumps(user_preferences),
                past_rituals=past_rituals_summary
            )
            
            # Add to conversation history
            self.conversation_history["ritual_advisor"].append({
                "timestamp": datetime.now(),
                "mood": user_mood,
                "task_type": task_type,
                "time": time_of_day
            })
            
            response = await self.llm.apredict(prompt)
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error generating ritual suggestion: {e}")
            # Fallback ritual
            return {
                "ritual_name": "Simple Focus Ritual",
                "duration_minutes": 3,
                "steps": [
                    {
                        "action": "Take 3 deep breaths to center yourself",
                        "duration_seconds": 30,
                        "type": "physical"
                    },
                    {
                        "action": "Clear your workspace of distractions",
                        "duration_seconds": 60,
                        "type": "environmental"
                    },
                    {
                        "action": "Set intention for this work session",
                        "duration_seconds": 30,
                        "type": "mental"
                    }
                ],
                "spotify_suggestion": {
                    "playlist_mood": "focus",
                    "duration": "during_work"
                },
                "why_this_works": "Simple preparation helps transition into focused work mode",
                "variations": ["Add gentle background music", "Include a quick stretch"]
            }
    
    def _format_past_rituals(self, past_rituals: List[Dict]) -> str:
        """Format past ritual data for agent context"""
        if not past_rituals:
            return "No previous ritual data available"
        
        summary = []
        for ritual in past_rituals[-3:]:  # Last 3 rituals
            name = ritual.get("name", "Unknown ritual")
            effectiveness = ritual.get("effectiveness_rating", "unknown")
            summary.append(f"- {name}: {effectiveness}/5 effectiveness")
        
        return "\n".join(summary)
    
    # ===== AGENT COORDINATION =====
    async def get_comprehensive_task_guidance(self, task_data: Dict[str, Any], 
                                            user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multiple agents for comprehensive task guidance"""
        try:
            task_title = task_data.get("title", "")
            task_description = task_data.get("description", "")
            duration = task_data.get("duration_minutes", 25)
            
            # Get analysis from multiple agents
            results = {}
            
            # Task analysis
            results["analysis"] = await self.get_task_analysis(
                task_title, task_description, duration,
                user_context.get("skill_level", "intermediate")
            )
            
            # Detailed breakdown
            results["breakdown"] = await self.decompose_task_detailed(
                f"{task_title}: {task_description}", duration, user_context
            )
            
            # Motivation
            results["motivation"] = await self.get_motivational_message(
                user_context,
                user_context.get("current_mood", "neutral"),
                user_context.get("recent_tasks", []),
                user_context.get("challenge", "")
            )
            
            # Ritual suggestion
            results["ritual"] = await self.suggest_ritual(
                user_context.get("current_mood", "neutral"),
                results["analysis"].get("energy_type", "analytical"),
                user_context.get("time_of_day", "morning"),
                user_context.get("preferences", {}),
                user_context.get("past_rituals", [])
            )
            
            return {
                "success": True,
                "guidance": results,
                "agent_recommendations": {
                    "difficulty_score": results["analysis"]["difficulty_score"],
                    "recommended_approach": results["analysis"]["energy_type"],
                    "procrastination_risk": results["analysis"]["procrastination_risk"],
                    "suggested_blocks": len(results["breakdown"]),
                    "ritual_duration": results["ritual"]["duration_minutes"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive task guidance: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_guidance": {
                    "message": "Unable to generate comprehensive guidance, but you can still start working!",
                    "basic_tip": "Break the task into smaller parts and take breaks every 25 minutes."
                }
            }
    
    # ===== MEMORY MANAGEMENT =====
    def clear_agent_memory(self, agent_name: str = None):
        """Clear memory for specific agent or all agents"""
        if agent_name and agent_name in self.conversation_history:
            self.conversation_history[agent_name] = []
        elif agent_name is None:
            for key in self.conversation_history:
                self.conversation_history[key] = []
    
    def get_agent_conversation_history(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get conversation history for specific agent"""
        if agent_name in self.conversation_history:
            return self.conversation_history[agent_name]
        return []
    
    # ===== UTILITY METHODS =====
    async def analyze_user_patterns(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user patterns to improve agent recommendations"""
        try:
            # Analyze task completion patterns
            completed_tasks = user_data.get("completed_tasks", [])
            failed_tasks = user_data.get("failed_tasks", [])
            
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
    
    def _analyze_task_preferences(self, completed_tasks: List[Dict]) -> Dict[str, Any]:
        """Analyze what types of tasks user completes successfully"""
        if not completed_tasks:
            return {"categories": [], "avg_duration": 25}
        
        categories = {}
        durations = []
        
        for task in completed_tasks:
            category = task.get("category", "general")
            categories[category] = categories.get(category, 0) + 1
            durations.append(task.get("duration_minutes", 25))
        
        return {
            "categories": sorted(categories.items(), key=lambda x: x[1], reverse=True),
            "avg_duration": sum(durations) / len(durations),
            "preferred_length": "short" if sum(durations) / len(durations) < 30 else "long"
        }
    
    def _analyze_difficulty_patterns(self, completed_tasks: List[Dict]) -> Dict[str, Any]:
        """Analyze user's difficulty comfort zone"""
        if not completed_tasks:
            return {"avg_difficulty": 1.0, "comfort_zone": "medium"}
        
        difficulties = [task.get("difficulty_score", 1.0) for task in completed_tasks]
        avg_difficulty = sum(difficulties) / len(difficulties)
        
        comfort_zone = "low"
        if avg_difficulty > 1.5:
            comfort_zone = "medium"
        if avg_difficulty > 2.0:
            comfort_zone = "high"
        
        return {
            "avg_difficulty": avg_difficulty,
            "comfort_zone": comfort_zone,
            "range": [min(difficulties), max(difficulties)]
        }
    
    def _analyze_time_patterns(self, completed_tasks: List[Dict]) -> Dict[str, Any]:
        """Analyze when user is most productive"""
        if not completed_tasks:
            return {"best_time": "morning", "pattern": "unknown"}
        
        # Simple time analysis - in real implementation, would use actual completion times
        return {
            "best_time": "morning",  # Placeholder
            "pattern": "consistent",  # Placeholder
            "total_completed": len(completed_tasks)
        }
    
    # ===== MCP ENHANCED METHODS =====
    
    async def decompose_task_mcp(self, task_description: str, duration_minutes: int, 
                                user_context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Enhanced task decomposition using MCP if available"""
        if self.use_mcp:
            try:
                async with MCPSession() as mcp:
                    result = await mcp.get_task_breakdown(
                        title=task_description.split(":")[0],
                        description=task_description.split(":", 1)[1] if ":" in task_description else "",
                        duration_minutes=duration_minutes,
                        user_context=user_context
                    )
                    
                    if result.get("success"):
                        return result.get("breakdown", [])
                    else:
                        logger.warning(f"MCP task breakdown failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"MCP task breakdown error: {e}")
        
        # Fallback to direct LLM call
        return await self.decompose_task_detailed(task_description, duration_minutes, user_context)
    
    async def get_task_analysis_mcp(self, task_title: str, description: str, 
                                   duration_minutes: int, user_skill_level: str = "intermediate") -> Dict[str, Any]:
        """Enhanced task analysis using MCP if available"""
        if self.use_mcp:
            try:
                async with MCPSession() as mcp:
                    result = await mcp.get_task_analysis(
                        title=task_title,
                        description=description,
                        duration_minutes=duration_minutes,
                        user_skill_level=user_skill_level
                    )
                    
                    if result.get("success"):
                        return result.get("analysis", {})
                    else:
                        logger.warning(f"MCP task analysis failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"MCP task analysis error: {e}")
        
        # Fallback to direct LLM call
        return await self.get_task_analysis(task_title, description, duration_minutes, user_skill_level)
    
    async def get_motivational_message_mcp(self, user_id: str, user_context: Dict[str, Any], 
                                          mood: str, current_challenge: str = "") -> str:
        """Enhanced motivation using MCP if available"""
        if self.use_mcp:
            try:
                async with MCPSession() as mcp:
                    result = await mcp.get_motivation(
                        user_id=user_id,
                        current_mood=mood,
                        challenge=current_challenge,
                        context=user_context
                    )
                    
                    if result.get("success"):
                        return result.get("motivation", "")
                    else:
                        logger.warning(f"MCP motivation failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"MCP motivation error: {e}")
        
        # Fallback to direct LLM call
        return await self.get_motivational_message(user_context, mood, [], current_challenge)
    
    async def validate_task_proof_mcp(self, task_description: str, proof_text: str, 
                                     completion_criteria: str = "") -> Dict[str, Any]:
        """Enhanced proof validation using MCP if available"""
        if self.use_mcp:
            try:
                async with MCPSession() as mcp:
                    result = await mcp.validate_proof(
                        task_description=task_description,
                        proof_text=proof_text,
                        completion_criteria=completion_criteria
                    )
                    
                    if result.get("success"):
                        return result.get("validation", {})
                    else:
                        logger.warning(f"MCP proof validation failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"MCP proof validation error: {e}")
        
        # Fallback to direct LLM call
        return await self.validate_task_proof(task_description, proof_text, completion_criteria)
    
    async def suggest_ritual_mcp(self, user_mood: str, task_type: str, 
                                time_of_day: str, user_preferences: Dict = None) -> Dict[str, Any]:
        """Enhanced ritual suggestion using MCP if available"""
        if self.use_mcp:
            try:
                async with MCPSession() as mcp:
                    result = await mcp.get_ritual_suggestion(
                        user_mood=user_mood,
                        task_type=task_type,
                        time_of_day=time_of_day,
                        preferences=user_preferences or {}
                    )
                    
                    if result.get("success"):
                        return result.get("ritual", {})
                    else:
                        logger.warning(f"MCP ritual suggestion failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"MCP ritual suggestion error: {e}")
        
        # Fallback to direct LLM call
        return await self.suggest_ritual(user_mood, task_type, time_of_day, user_preferences, [])
    
    async def get_comprehensive_task_guidance_mcp(self, user_id: str, task_data: Dict[str, Any], 
                                                 user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced comprehensive guidance using MCP if available"""
        if self.use_mcp:
            try:
                async with MCPSession() as mcp:
                    result = await mcp.get_comprehensive_guidance(
                        user_id=user_id,
                        task_data=task_data,
                        user_context=user_context
                    )
                    
                    if result.get("success"):
                        return result.get("guidance", {})
                    else:
                        logger.warning(f"MCP comprehensive guidance failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"MCP comprehensive guidance error: {e}")
        
        # Fallback to direct LLM call
        return await self.get_comprehensive_task_guidance(task_data, user_context)
    
    def toggle_mcp(self, enabled: bool):
        """Toggle MCP integration on/off"""
        self.use_mcp = enabled
        logger.info(f"MCP integration {'enabled' if enabled else 'disabled'}")
    
    async def get_mcp_status(self) -> Dict[str, Any]:
        """Get MCP connection status and available tools"""
        if not self.use_mcp:
            return {"enabled": False, "connected": False, "tools": [], "mode": "disabled"}
        
        try:
            # Try to get status from simplified server first
            async with MCPSession() as mcp:
                if hasattr(mcp, 'simplified_server') and mcp.simplified_server:
                    # Using simplified server
                    tools = list(mcp.simplified_server.tools.keys())
                    tool_details = [
                        {
                            "name": name,
                            "description": info.get("description", ""),
                            "parameters": info.get("parameters", {})
                        }
                        for name, info in mcp.simplified_server.tools.items()
                    ]
                    
                    return {
                        "enabled": True,
                        "connected": True,
                        "mode": "simplified_server",
                        "tools": tool_details,
                        "tool_count": len(tools),
                        "message": "MCP running with simplified internal server"
                    }
                else:
                    # Try external MCP server
                    tools = await mcp.list_tools()
                    return {
                        "enabled": True,
                        "connected": True,
                        "mode": "external_server",
                        "tools": tools,
                        "tool_count": len(tools),
                        "message": "MCP running with external server"
                    }
        except Exception as e:
            logger.warning(f"MCP server connection failed: {e}")
            # Fallback to mock tools
            tools = [
                {"name": "task_breakdown", "description": "Break down tasks into manageable steps"},
                {"name": "motivation_coach", "description": "Provide motivational support"},
                {"name": "task_analysis", "description": "Analyze task complexity"},
                {"name": "proof_validation", "description": "Validate task completion proof"},
                {"name": "ritual_suggestion", "description": "Suggest productivity rituals"},
                {"name": "comprehensive_guidance", "description": "Comprehensive AI guidance"},
                {"name": "create_task", "description": "Create new tasks"},
                {"name": "log_mood", "description": "Log mood entries"},
                {"name": "get_focus_playlist", "description": "Get Spotify focus playlist"}
            ]
            
            return {
                "enabled": True,
                "connected": False,
                "mode": "fallback",
                "tools": tools,
                "tool_count": len(tools),
                "error": str(e),
                "message": "MCP using fallback mode due to connection issues"
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
