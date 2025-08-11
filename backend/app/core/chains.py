"""
Chains layer for Memory-Chain-Planner architecture
Implements specialized LangChain chains for task management workflows
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from langchain.chains.base import Chain
from langchain.chains import SequentialChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import BaseOutputParser
from langchain.llms.base import BaseLLM
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.manager import CallbackManagerForChainRun
from pydantic import BaseModel, Field

from app.core.memory import memory_manager
from app.core.config import settings
from app.core.unified_mcp import unified_mcp

logger = logging.getLogger(__name__)


class TaskBreakdownOutput(BaseModel):
    """Output model for task breakdown chain"""
    blocks: List[Dict[str, Any]]
    total_duration: int
    complexity_score: float
    recommendations: List[str]


class TaskAnalysisOutput(BaseModel):
    """Output model for task analysis chain"""
    difficulty: str
    estimated_time: int
    required_skills: List[str]
    potential_obstacles: List[str]
    success_probability: float


class MotivationOutput(BaseModel):
    """Output model for motivation chain"""
    message: str
    mood_boost_level: int
    suggested_actions: List[str]
    follow_up_timing: int


class ProofValidationOutput(BaseModel):
    """Output model for proof validation chain"""
    is_valid: bool
    confidence_score: float
    validation_notes: str
    improvement_suggestions: List[str]


class BaseTaskChain(Chain):
    """Base class for task-related chains with memory integration"""
    
    llm: BaseLLM = Field(default_factory=lambda: ChatOpenAI(
        model="gpt-4",
        temperature=0.3,
        openai_api_key=settings.OPENAI_API_KEY
    ))
    memory_enabled: bool = Field(default=True)
    user_id: str = Field(default="default")
    
    @property
    def input_keys(self) -> List[str]:
        """Input keys required by the chain"""
        return ["input"]
    
    @property 
    def output_keys(self) -> List[str]:
        """Output keys provided by the chain"""
        return ["output"]
    
    async def _get_user_context(self) -> Dict[str, Any]:
        """Get user context from memory"""
        if not self.memory_enabled:
            return {}
        
        return await memory_manager.get_user_context(self.user_id)
    
    async def _store_chain_result(self, chain_name: str, inputs: Dict, outputs: Dict):
        """Store chain execution result in memory"""
        if not self.memory_enabled:
            return
        
        result_data = {
            "chain_name": chain_name,
            "inputs": inputs,
            "outputs": outputs,
            "timestamp": datetime.now().isoformat(),
            "user_id": self.user_id
        }
        
        await memory_manager.memory_store.store_memory(
            "working",
            f"chain_result:{chain_name}:{datetime.now().timestamp()}",
            result_data,
            self.user_id
        )


class TaskBreakdownChain(BaseTaskChain):
    """
    Specialized chain for breaking down tasks into manageable blocks
    Integrates with MCP and uses memory for context
    """
    
    prompt_template: str = """
    You are an expert task breakdown specialist. Break down the following task into manageable blocks.
    
    Task Information:
    Title: {title}
    Description: {description}
    Total Duration: {duration_minutes} minutes
    
    User Context:
    {user_context}
    
    Past Similar Tasks:
    {similar_tasks}
    
    Please break this task into blocks of 25-45 minutes each. For each block, provide:
    1. Block title
    2. Specific objectives
    3. Estimated duration
    4. Prerequisites
    5. Success criteria
    
    Return your response as a JSON object with the following structure:
    {{
        "blocks": [
            {{
                "title": "Block title",
                "objectives": ["objective1", "objective2"],
                "duration_minutes": 30,
                "prerequisites": ["prereq1"],
                "success_criteria": ["criteria1", "criteria2"]
            }}
        ],
        "total_duration": {duration_minutes},
        "complexity_score": 0.7,
        "recommendations": ["recommendation1", "recommendation2"]
    }}
    """
    
    @property
    def input_keys(self) -> List[str]:
        return ["title", "description", "duration_minutes"]
    
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute the task breakdown chain"""
        # This is the sync wrapper - actual implementation will be async
        return asyncio.run(self._acall(inputs, run_manager))
    
    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Async execution of task breakdown"""
        
        # Get user context and similar tasks from memory
        user_context = await self._get_user_context()
        similar_tasks = await memory_manager.search_similar_tasks(
            self.user_id, 
            inputs.get("description", ""),
            limit=3
        )
        
        # Format similar tasks for prompt
        similar_tasks_text = "\n".join([
            f"- {task.get('value', {}).get('description', 'No description')}"
            for task in similar_tasks
        ]) or "No similar tasks found"
        
        # Create prompt
        prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["title", "description", "duration_minutes", "user_context", "similar_tasks"]
        )
        
        # Format inputs
        formatted_inputs = {
            **inputs,
            "user_context": json.dumps(user_context, indent=2),
            "similar_tasks": similar_tasks_text
        }
        
        # Create and run chain
        chain = prompt | self.llm
        
        try:
            result = await chain.ainvoke(formatted_inputs)
            
            # Parse JSON response from the chain output
            chain_output = result.content if hasattr(result, 'content') else str(result)
            parsed_result = json.loads(chain_output)
            
            # Store result in memory
            await self._store_chain_result("task_breakdown", inputs, parsed_result)
            
            # Also use MCP to validate/enhance the breakdown
            try:
                mcp_result = await unified_mcp.call_tool(
                    "task_breakdown",
                    {
                        "title": inputs["title"],
                        "description": inputs.get("description", ""),
                        "duration_minutes": inputs["duration_minutes"],
                        "user_context": user_context
                    }
                )
                
                if mcp_result.get("success"):
                    # Enhance with MCP insights
                    mcp_breakdown = mcp_result.get("result", {}).get("blocks", [])
                    if mcp_breakdown:
                        parsed_result["mcp_enhanced"] = True
                        parsed_result["mcp_blocks"] = mcp_breakdown
                
            except Exception as e:
                logger.warning(f"MCP enhancement failed: {e}")
            
            return {"output": parsed_result}
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            # Fallback to simple breakdown
            return {"output": self._create_fallback_breakdown(inputs)}
        except Exception as e:
            logger.error(f"Task breakdown chain failed: {e}")
            return {"output": self._create_fallback_breakdown(inputs)}
    
    def _create_fallback_breakdown(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create a simple fallback breakdown"""
        duration = inputs.get("duration_minutes", 60)
        block_count = max(1, duration // 30)
        block_duration = duration // block_count
        
        blocks = []
        for i in range(block_count):
            blocks.append({
                "title": f"Work Block {i + 1}",
                "objectives": [f"Work on {inputs.get('title', 'task')}"],
                "duration_minutes": block_duration,
                "prerequisites": [],
                "success_criteria": ["Complete assigned work"]
            })
        
        return {
            "blocks": blocks,
            "total_duration": duration,
            "complexity_score": 0.5,
            "recommendations": ["Take breaks between blocks", "Stay focused on objectives"]
        }


class TaskAnalysisChain(BaseTaskChain):
    """Chain for analyzing task complexity and requirements"""
    
    prompt_template: str = """
    Analyze the following task and provide detailed insights:
    
    Task: {title}
    Description: {description}
    Estimated Duration: {duration_minutes} minutes
    User Skill Level: {skill_level}
    
    User Context:
    {user_context}
    
    Provide analysis in JSON format:
    {{
        "difficulty": "easy|medium|hard|expert",
        "estimated_time": {duration_minutes},
        "required_skills": ["skill1", "skill2"],
        "potential_obstacles": ["obstacle1", "obstacle2"],
        "success_probability": 0.85,
        "time_adjustment_factor": 1.0,
        "recommendations": ["rec1", "rec2"]
    }}
    """
    
    @property
    def input_keys(self) -> List[str]:
        return ["title", "description", "duration_minutes", "skill_level"]
    
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute the task analysis chain (sync wrapper)"""
        return asyncio.run(self._acall(inputs, run_manager))
    
    async def _acall(self, inputs: Dict[str, Any], run_manager = None) -> Dict[str, Any]:
        """Async execution of task analysis"""
        
        user_context = await self._get_user_context()
        
        prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["title", "description", "duration_minutes", "skill_level", "user_context"]
        )
        
        formatted_inputs = {
            **inputs,
            "user_context": json.dumps(user_context, indent=2)
        }
        
        # Use the new RunnableSequence pattern instead of deprecated LLMChain
        chain = prompt | self.llm
        
        try:
            result = await chain.ainvoke(formatted_inputs)
            chain_output = result.content if hasattr(result, 'content') else str(result)
            parsed_result = json.loads(chain_output)
            
            await self._store_chain_result("task_analysis", inputs, parsed_result)
            
            return {"output": parsed_result}
            
        except Exception as e:
            logger.error(f"Task analysis chain failed: {e}")
            return {"output": self._create_fallback_analysis(inputs)}
    
    def _create_fallback_analysis(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback analysis"""
        duration = inputs.get("duration_minutes", 60)
        
        if duration <= 30:
            difficulty = "easy"
            success_prob = 0.9
        elif duration <= 120:
            difficulty = "medium"
            success_prob = 0.75
        else:
            difficulty = "hard"
            success_prob = 0.6
        
        return {
            "difficulty": difficulty,
            "estimated_time": duration,
            "required_skills": ["focus", "time management"],
            "potential_obstacles": ["distractions", "complexity"],
            "success_probability": success_prob,
            "time_adjustment_factor": 1.0,
            "recommendations": ["Break into smaller chunks", "Minimize distractions"]
        }


class MotivationChain(BaseTaskChain):
    """Chain for generating personalized motivation"""
    
    prompt_template: str = """
    Generate personalized motivation for the user based on their current situation:
    
    User Context:
    {user_context}
    
    Current Mood: {mood}
    Current Challenge: {challenge}
    Recent Accomplishments: {accomplishments}
    
    Create motivational content that:
    1. Acknowledges their current state
    2. Provides encouragement
    3. Suggests specific actions
    4. Sets positive expectations
    
    Return JSON format:
    {{
        "message": "Personalized motivational message",
        "mood_boost_level": 7,
        "suggested_actions": ["action1", "action2"],
        "follow_up_timing": 30,
        "tone": "encouraging|energetic|calm|supportive"
    }}
    """
    
    @property
    def input_keys(self) -> List[str]:
        return ["mood", "challenge", "accomplishments"]
    
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute the motivation chain (sync wrapper)"""
        return asyncio.run(self._acall(inputs, run_manager))
    
    async def _acall(self, inputs: Dict[str, Any], run_manager = None) -> Dict[str, Any]:
        """Generate personalized motivation"""
        
        user_context = await self._get_user_context()
        
        prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["user_context", "mood", "challenge", "accomplishments"]
        )
        
        formatted_inputs = {
            **inputs,
            "user_context": json.dumps(user_context, indent=2),
            "accomplishments": json.dumps(inputs.get("accomplishments", []))
        }
        
        chain = prompt | self.llm
        
        try:
            result = await chain.ainvoke(formatted_inputs)
            chain_output = result.content if hasattr(result, 'content') else str(result)
            parsed_result = json.loads(chain_output)
            
            await self._store_chain_result("motivation", inputs, parsed_result)
            
            return {"output": parsed_result}
            
        except Exception as e:
            logger.error(f"Motivation chain failed: {e}")
            return {"output": self._create_fallback_motivation(inputs)}
    
    def _create_fallback_motivation(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback motivation"""
        mood = inputs.get("mood", "neutral")
        
        messages = {
            "low": "Every small step counts. You're building momentum!",
            "neutral": "You're doing great! Keep the steady progress going.",
            "high": "Your energy is amazing! Channel it into focused action!"
        }
        
        return {
            "message": messages.get(mood, messages["neutral"]),
            "mood_boost_level": 6,
            "suggested_actions": ["Take a deep breath", "Start with one small task"],
            "follow_up_timing": 30,
            "tone": "supportive"
        }


class ProofValidationChain(BaseTaskChain):
    """Chain for validating task completion proofs"""
    
    prompt_template: str = """
    Validate whether the provided proof demonstrates task completion:
    
    Task: {task_description}
    Completion Criteria: {completion_criteria}
    Proof Provided: {proof_text}
    
    Analyze the proof and determine if it satisfactorily demonstrates task completion.
    
    Return JSON format:
    {{
        "is_valid": true,
        "confidence_score": 0.95,
        "validation_notes": "Detailed explanation of validation",
        "improvement_suggestions": ["suggestion1", "suggestion2"],
        "partial_credit": 0.8,
        "requires_manual_review": false
    }}
    """
    
    @property
    def input_keys(self) -> List[str]:
        return ["task_description", "completion_criteria", "proof_text"]
    
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute the proof validation chain (sync wrapper)"""
        return asyncio.run(self._acall(inputs, run_manager))
    
    async def _acall(self, inputs: Dict[str, Any], run_manager = None) -> Dict[str, Any]:
        """Validate task completion proof"""
        
        prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["task_description", "completion_criteria", "proof_text"]
        )
        
        chain = prompt | self.llm
        
        try:
            result = await chain.ainvoke(inputs)
            chain_output = result.content if hasattr(result, 'content') else str(result)
            parsed_result = json.loads(chain_output)
            
            await self._store_chain_result("proof_validation", inputs, parsed_result)
            
            return {"output": parsed_result}
            
        except Exception as e:
            logger.error(f"Proof validation chain failed: {e}")
            return {"output": self._create_fallback_validation(inputs)}
    
    def _create_fallback_validation(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback validation"""
        proof_text = inputs.get("proof_text", "")
        
        # Simple heuristics
        has_content = len(proof_text.strip()) > 10
        confidence = 0.7 if has_content else 0.3
        
        return {
            "is_valid": has_content,
            "confidence_score": confidence,
            "validation_notes": "Automated validation based on content length",
            "improvement_suggestions": ["Provide more detailed proof"] if not has_content else [],
            "partial_credit": confidence,
            "requires_manual_review": confidence < 0.8
        }


class ChainExecutor:
    """
    Central chain execution manager
    Handles chain composition, caching, and error recovery
    """
    
    def __init__(self):
        self.chains = {
            "task_breakdown": TaskBreakdownChain,
            "task_analysis": TaskAnalysisChain,
            "motivation": MotivationChain,
            "proof_validation": ProofValidationChain
        }
        self.cache = {}
        self.cache_ttl = 1800  # 30 minutes
    
    async def execute_chain(self, chain_name: str, inputs: Dict[str, Any], 
                           user_id: str = "default", use_cache: bool = True) -> Dict[str, Any]:
        """Execute a specific chain with caching"""
        
        # Check cache
        cache_key = f"{chain_name}:{user_id}:{hash(str(sorted(inputs.items())))}"
        if use_cache and cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if (datetime.now().timestamp() - timestamp) < self.cache_ttl:
                logger.info(f"Returning cached result for {chain_name}")
                return cached_result
        
        # Execute chain
        if chain_name not in self.chains:
            raise ValueError(f"Unknown chain: {chain_name}")
        
        chain_class = self.chains[chain_name]
        chain = chain_class(user_id=user_id)
        
        try:
            result = await chain._acall(inputs)
            
            # Cache result
            if use_cache:
                self.cache[cache_key] = (result, datetime.now().timestamp())
            
            return result
            
        except Exception as e:
            logger.error(f"Chain execution failed for {chain_name}: {e}")
            raise
    
    async def execute_chain_sequence(self, chain_specs: List[Dict[str, Any]], 
                                   user_id: str = "default") -> List[Dict[str, Any]]:
        """Execute a sequence of chains"""
        results = []
        
        for spec in chain_specs:
            chain_name = spec["chain"]
            inputs = spec["inputs"]
            
            # Merge previous results if specified
            if "merge_from" in spec:
                merge_index = spec["merge_from"]
                if 0 <= merge_index < len(results):
                    inputs.update(results[merge_index].get("output", {}))
            
            result = await self.execute_chain(chain_name, inputs, user_id)
            results.append(result)
        
        return results
    
    def clear_cache(self, chain_name: str = None, user_id: str = None):
        """Clear chain cache"""
        if chain_name is None and user_id is None:
            self.cache.clear()
        else:
            keys_to_remove = []
            for key in self.cache.keys():
                if chain_name and not key.startswith(f"{chain_name}:"):
                    continue
                if user_id and f":{user_id}:" not in key:
                    continue
                keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.cache[key]


# Global chain executor instance
chain_executor = ChainExecutor()
