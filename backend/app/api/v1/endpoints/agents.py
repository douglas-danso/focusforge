from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from app.services.llm_service import LLMService
from app.services.task_service import TaskService
from app.core.database import get_database

router = APIRouter()

@router.post("/task-breakdown", response_model=Dict[str, Any])
async def get_task_breakdown(
    task_data: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
    detailed: bool = Query(False, description="Return detailed breakdown with full block info")
):
    """Get AI-powered task breakdown from TaskBreakdownAgent"""
    try:
        llm_service = LLMService()
        
        title = task_data.get("title", "")
        description = task_data.get("description", "")
        duration = task_data.get("duration_minutes", 25)
        
        if detailed:
            breakdown = await llm_service.decompose_task_detailed(
                f"{title}: {description}", duration, user_context
            )
        else:
            breakdown = await llm_service.decompose_task(
                f"{title}: {description}", duration, user_context
            )
        
        return {
            "success": True,
            "breakdown": breakdown,
            "task_info": task_data,
            "detailed": detailed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/task-analysis", response_model=Dict[str, Any])
async def get_task_analysis(
    task_data: Dict[str, Any],
    user_skill_level: str = Query("intermediate", description="User's skill level")
):
    """Get comprehensive task analysis from TaskWeightingAgent"""
    try:
        llm_service = LLMService()
        
        analysis = await llm_service.get_task_analysis(
            task_title=task_data.get("title", ""),
            description=task_data.get("description", ""),
            duration_minutes=task_data.get("duration_minutes", 25),
            user_skill_level=user_skill_level
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "task_info": task_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/motivation", response_model=Dict[str, Any])
async def get_motivation(
    user_context: Dict[str, Any],
    mood: str = Query("neutral", description="Current mood"),
    challenge: str = Query("", description="Current challenge or obstacle"),
    task_history: Optional[List[Dict]] = None
):
    """Get personalized motivation from MotivationCoachAgent"""
    try:
        llm_service = LLMService()
        
        message = await llm_service.get_motivational_message(
            user_context=user_context,
            mood=mood,
            task_history=task_history or [],
            current_challenge=challenge
        )
        
        return {
            "success": True,
            "message": message,
            "mood": mood,
            "challenge": challenge
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/proof-validation", response_model=Dict[str, Any])
async def validate_proof(
    validation_data: Dict[str, Any]
):
    """Validate task completion proof using ProofVerificationAgent"""
    try:
        llm_service = LLMService()
        
        result = await llm_service.validate_task_proof(
            task_description=validation_data.get("task_description", ""),
            proof_text=validation_data.get("proof_text", ""),
            completion_criteria=validation_data.get("completion_criteria", "")
        )
        
        return {
            "success": True,
            "validation": result,
            "task_description": validation_data.get("task_description", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ritual-suggestion", response_model=Dict[str, Any])
async def get_ritual_suggestion(
    ritual_request: Dict[str, Any]
):
    """Get personalized productivity ritual from RitualAdvisorAgent"""
    try:
        llm_service = LLMService()
        
        ritual = await llm_service.suggest_ritual(
            user_mood=ritual_request.get("mood", "neutral"),
            task_type=ritual_request.get("task_type", "general"),
            time_of_day=ritual_request.get("time_of_day", "morning"),
            user_preferences=ritual_request.get("preferences", {}),
            past_rituals=ritual_request.get("past_rituals", [])
        )
        
        return {
            "success": True,
            "ritual": ritual,
            "request_info": ritual_request
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comprehensive-guidance", response_model=Dict[str, Any])
async def get_comprehensive_guidance(
    task_data: Dict[str, Any],
    user_context: Dict[str, Any]
):
    """Get comprehensive guidance from all agents working together"""
    try:
        llm_service = LLMService()
        
        guidance = await llm_service.get_comprehensive_task_guidance(
            task_data=task_data,
            user_context=user_context
        )
        
        return guidance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-patterns", response_model=Dict[str, Any])
async def analyze_user_patterns(
    user_data: Dict[str, Any],
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Analyze user patterns to improve agent recommendations"""
    try:
        llm_service = LLMService()
        task_service = TaskService(db)
        
        # Enhance user data with task statistics
        user_stats = await task_service._get_user_task_stats(user_id)
        enhanced_user_data = {**user_data, "stats": user_stats}
        
        patterns = await llm_service.analyze_user_patterns(enhanced_user_data)
        
        return {
            "success": True,
            "patterns": patterns,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent-memory/clear", response_model=Dict[str, Any])
async def clear_agent_memory(
    agent_name: Optional[str] = Query(None, description="Specific agent to clear, or all if not provided")
):
    """Clear conversation memory for agents"""
    try:
        llm_service = LLMService()
        llm_service.clear_agent_memory(agent_name)
        
        return {
            "success": True,
            "message": f"Memory cleared for {agent_name or 'all agents'}",
            "agent": agent_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-memory/{agent_name}", response_model=Dict[str, Any])
async def get_agent_memory(
    agent_name: str
):
    """Get conversation history for a specific agent"""
    try:
        llm_service = LLMService()
        history = llm_service.get_agent_conversation_history(agent_name)
        
        return {
            "success": True,
            "agent": agent_name,
            "conversation_history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
