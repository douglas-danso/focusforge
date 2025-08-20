"""
Custom Ritual API endpoints for FocusForge
Provides comprehensive ritual creation, execution, and management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.ritual_service import RitualService
from app.models.schemas import RitualCreate, Ritual, RitualStep
from app.models.api_schemas import validate_user_id
from app.core.database import get_database
from app.core.auth import get_current_user_from_token

router = APIRouter()

# ===== RITUAL MANAGEMENT =====

@router.post("/", response_model=Dict[str, Any])
async def create_custom_ritual(
    ritual_data: RitualCreate,
    user_id: str = Depends(get_current_user_from_token),
    db=Depends(get_database)
):
    """Create a custom focus ritual"""
    try:
        user_id = validate_user_id(user_id)
        ritual_service = RitualService(db)
        await ritual_service.initialize()
        
        ritual = await ritual_service.create_custom_ritual(user_id, ritual_data)
        
        return {
            "success": True,
            "ritual": {
                "id": ritual.id,
                "name": ritual.name,
                "description": ritual.description,
                "category": ritual.category,
                "estimated_duration_minutes": ritual.estimated_duration_minutes,
                "total_steps": len(ritual.steps),
                "tags": ritual.tags,
                "is_public": ritual.is_public,
                "created_at": ritual.created_at.isoformat()
            },
            "message": f"Custom ritual '{ritual.name}' created successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ritual: {str(e)}")

@router.get("/", response_model=List[Dict[str, Any]])
async def get_user_rituals(
    user_id: str = Depends(get_current_user_from_token),
    include_public: bool = Query(True, description="Include public rituals"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db=Depends(get_database)
):
    """Get user's custom rituals"""
    try:
        user_id = validate_user_id(user_id)
        ritual_service = RitualService(db)
        await ritual_service.initialize()
        
        rituals = await ritual_service.get_user_rituals(user_id, include_public, category)
        
        return [
            {
                "id": ritual.id,
                "name": ritual.name,
                "description": ritual.description,
                "category": ritual.category,
                "estimated_duration_minutes": ritual.estimated_duration_minutes,
                "total_steps": len(ritual.steps),
                "tags": ritual.tags,
                "is_public": ritual.is_public,
                "is_own_ritual": ritual.user_id == user_id,
                "usage_count": ritual.usage_count,
                "avg_effectiveness": (
                    sum(ritual.effectiveness_ratings) / len(ritual.effectiveness_ratings)
                    if ritual.effectiveness_ratings else 0
                ),
                "created_at": ritual.created_at.isoformat(),
                "updated_at": ritual.updated_at.isoformat()
            }
            for ritual in rituals
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rituals: {str(e)}")

@router.get("/{ritual_id}")
async def get_ritual_details(
    ritual_id: str = Path(..., description="Ritual ID"),
    user_id: str = Depends(get_current_user_from_token),
    db=Depends(get_database)
):
    """Get detailed information about a specific ritual"""
    try:
        user_id = validate_user_id(user_id)
        ritual_service = RitualService(db)
        await ritual_service.initialize()
        
        ritual = await ritual_service.get_ritual_by_id(ritual_id, user_id)
        
        if not ritual:
            raise HTTPException(status_code=404, detail="Ritual not found")
        
        return {
            "success": True,
            "ritual": {
                "id": ritual.id,
                "name": ritual.name,
                "description": ritual.description,
                "category": ritual.category,
                "estimated_duration_minutes": ritual.estimated_duration_minutes,
                "tags": ritual.tags,
                "is_public": ritual.is_public,
                "is_own_ritual": ritual.user_id == user_id,
                "usage_count": ritual.usage_count,
                "effectiveness_ratings": ritual.effectiveness_ratings,
                "avg_effectiveness": (
                    sum(ritual.effectiveness_ratings) / len(ritual.effectiveness_ratings)
                    if ritual.effectiveness_ratings else 0
                ),
                "created_at": ritual.created_at.isoformat(),
                "updated_at": ritual.updated_at.isoformat(),
                "steps": [
                    {
                        "step_type": step.step_type,
                        "title": step.title,
                        "description": step.description,
                        "duration_seconds": step.duration_seconds,
                        "duration_minutes": round(step.duration_seconds / 60, 1),
                        "spotify_playlist_id": step.spotify_playlist_id,
                        "spotify_search_query": step.spotify_search_query,
                        "meditation_type": step.meditation_type,
                        "meditation_voice": step.meditation_voice,
                        "meditation_background": step.meditation_background,
                        "breathing_pattern": step.breathing_pattern,
                        "setup_instructions": step.setup_instructions,
                        "custom_instructions": step.custom_instructions
                    }
                    for step in ritual.steps
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ritual details: {str(e)}")

# ===== RITUAL EXECUTION =====

@router.post("/{ritual_id}/execute")
async def start_ritual_execution(
    ritual_id: str = Path(..., description="Ritual ID"),
    user_id: str = Depends(get_current_user_from_token),
    context: Optional[Dict[str, Any]] = None,
    db=Depends(get_database)
):
    """Start executing a custom ritual"""
    try:
        user_id = validate_user_id(user_id)
        ritual_service = RitualService(db)
        await ritual_service.initialize()
        
        result = await ritual_service.execute_custom_ritual(user_id, ritual_id, context)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to start ritual"))
        
        return {
            **result,
            "instructions": [
                "Follow each step carefully",
                "Take your time with each activity",
                "Use the advance endpoint when ready for the next step",
                "Focus on the present moment during each step"
            ],
            "tips": [
                "Don't rush through the steps",
                "If a step isn't working, adapt it to your needs",
                "Rate each step to help improve future rituals",
                "Remember: this is your time for preparation and focus"
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start ritual: {str(e)}")

@router.post("/executions/{execution_id}/advance")
async def advance_ritual_step(
    execution_id: str = Path(..., description="Execution ID"),
    user_id: str = Depends(get_current_user_from_token),
    step_feedback: Optional[Dict[str, Any]] = None,
    db=Depends(get_database)
):
    """Advance to the next step in ritual execution"""
    try:
        user_id = validate_user_id(user_id)
        ritual_service = RitualService(db)
        await ritual_service.initialize()
        
        result = await ritual_service.advance_ritual_step(execution_id, user_id, step_feedback)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to advance step"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to advance ritual step: {str(e)}")

@router.post("/executions/{execution_id}/complete")
async def complete_ritual_execution(
    execution_id: str = Path(..., description="Execution ID"),
    user_id: str = Depends(get_current_user_from_token),
    effectiveness_rating: int = Query(..., ge=1, le=10, description="Effectiveness rating (1-10)"),
    notes: Optional[str] = Query(None, description="Optional notes about the ritual"),
    db=Depends(get_database)
):
    """Complete a ritual execution with feedback"""
    try:
        user_id = validate_user_id(user_id)
        ritual_service = RitualService(db)
        await ritual_service.initialize()
        
        # Update execution with rating and notes
        await ritual_service.executions_collection.update_one(
            {"_id": execution_id, "user_id": user_id},
            {
                "$set": {
                    "effectiveness_rating": effectiveness_rating,
                    "notes": notes or "",
                    "completed": True,
                    "completed_at": datetime.now()
                }
            }
        )
        
        # Update ritual's effectiveness ratings
        execution = await ritual_service.executions_collection.find_one({"_id": execution_id})
        if execution:
            await ritual_service.collection.update_one(
                {"_id": execution["ritual_id"]},
                {"$push": {"effectiveness_ratings": effectiveness_rating}}
            )
        
        return {
            "success": True,
            "message": "🎉 Ritual completed and feedback recorded!",
            "effectiveness_rating": effectiveness_rating,
            "notes": notes,
            "next_steps": [
                "You're now prepared for focused work",
                "Start your main task while in this focused state",
                "Remember to take breaks as needed",
                "Consider using this ritual again for similar tasks"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete ritual: {str(e)}")

# ===== RITUAL TEMPLATES =====

@router.get("/templates/")
async def get_ritual_templates(
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get pre-built ritual templates"""
    try:
        ritual_service = RitualService()
        templates = await ritual_service.get_ritual_templates(category)
        
        return {
            "success": True,
            "templates": templates,
            "total_templates": len(templates),
            "categories": list(set(t["category"] for t in templates)),
            "message": "Use these templates as starting points for your custom rituals"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

@router.post("/templates/{template_name}/create")
async def create_ritual_from_template(
    template_name: str = Path(..., description="Template name"),
    user_id: str = Depends(get_current_user_from_token),
    customizations: Optional[Dict[str, Any]] = None,
    db=Depends(get_database)
):
    """Create a custom ritual from a template"""
    try:
        user_id = validate_user_id(user_id)
        ritual_service = RitualService(db)
        await ritual_service.initialize()
        
        result = await ritual_service.create_ritual_from_template(
            user_id, template_name, customizations
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create from template"))
        
        return {
            **result,
            "customization_options": [
                "You can modify any step in your new ritual",
                "Add or remove steps as needed",
                "Adjust timing to fit your schedule",
                "Make it truly your own!"
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create from template: {str(e)}")

# ===== MEDITATION INTEGRATION =====

@router.post("/meditation/start")
async def start_meditation_session(
    user_id: str = Depends(get_current_user_from_token),
    meditation_type: str = Query("breathing", description="Meditation type"),
    duration_minutes: int = Query(5, ge=1, le=60, description="Duration in minutes"),
    guidance_voice: str = Query("calm_female", description="Guidance voice"),
    background_sound: str = Query("nature", description="Background sound"),
    mood_before: Optional[str] = Query(None, description="Mood before meditation"),
    db=Depends(get_database)
):
    """Start a standalone meditation session"""
    try:
        user_id = validate_user_id(user_id)
        ritual_service = RitualService(db)
        await ritual_service.initialize()
        
        session_data = {
            "type": meditation_type,
            "duration_minutes": duration_minutes,
            "guidance_voice": guidance_voice,
            "background_sound": background_sound,
            "mood_before": mood_before
        }
        
        result = await ritual_service.meditation_service.start_meditation_session(user_id, session_data)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to start meditation"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start meditation: {str(e)}")

@router.post("/meditation/{session_id}/complete")
async def complete_meditation_session(
    session_id: str = Path(..., description="Meditation session ID"),
    user_id: str = Depends(get_current_user_from_token),
    mood_after: Optional[str] = Query(None, description="Mood after meditation"),
    effectiveness_rating: int = Query(..., ge=1, le=10, description="Effectiveness rating (1-10)"),
    notes: Optional[str] = Query(None, description="Session notes"),
    db=Depends(get_database)
):
    """Complete a meditation session"""
    try:
        user_id = validate_user_id(user_id)
        ritual_service = RitualService(db)
        await ritual_service.initialize()
        
        completion_data = {
            "mood_after": mood_after,
            "rating": effectiveness_rating,
            "notes": notes
        }
        
        result = await ritual_service.meditation_service.complete_meditation_session(
            session_id, user_id, completion_data
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to complete meditation"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete meditation: {str(e)}")

# ===== ANALYTICS & INSIGHTS =====

@router.get("/analytics/usage")
async def get_ritual_analytics(
    user_id: str = Depends(get_current_user_from_token),
    days_back: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db=Depends(get_database)
):
    """Get ritual usage analytics and insights"""
    try:
        user_id = validate_user_id(user_id)
        ritual_service = RitualService(db)
        await ritual_service.initialize()
        
        analytics = await ritual_service.get_ritual_analytics(user_id, days_back)
        
        if not analytics.get("success"):
            raise HTTPException(status_code=500, detail=analytics.get("error", "Failed to get analytics"))
        
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/categories")
async def get_ritual_categories():
    """Get available ritual categories"""
    return {
        "categories": [
            {
                "name": "deep_work",
                "display_name": "Deep Work",
                "description": "Intensive focus for complex tasks",
                "icon": "🎯",
                "recommended_duration": "8-15 minutes"
            },
            {
                "name": "energy",
                "display_name": "Energy Boost",
                "description": "Quick energizing rituals",
                "icon": "⚡",
                "recommended_duration": "3-5 minutes"
            },
            {
                "name": "calm",
                "display_name": "Calm & Centered", 
                "description": "Stress relief and centering",
                "icon": "🧘‍♀️",
                "recommended_duration": "5-10 minutes"
            },
            {
                "name": "creative",
                "display_name": "Creative Flow",
                "description": "Enhance creativity and inspiration",
                "icon": "🎨",
                "recommended_duration": "5-8 minutes"
            },
            {
                "name": "study",
                "display_name": "Study Session",
                "description": "Preparation for learning and retention",
                "icon": "📚",
                "recommended_duration": "6-10 minutes"
            },
            {
                "name": "presentation",
                "display_name": "Presentation Prep",
                "description": "Confidence building for presentations",
                "icon": "🎤",
                "recommended_duration": "7-12 minutes"
            }
        ]
    }

@router.get("/step-types")
async def get_ritual_step_types():
    """Get available ritual step types and their configurations"""
    return {
        "step_types": [
            {
                "type": "environment_setup",
                "display_name": "Environment Setup",
                "description": "Prepare your physical workspace",
                "icon": "🏠",
                "typical_duration": "60-180 seconds",
                "required_fields": ["title", "description"],
                "optional_fields": ["setup_instructions"]
            },
            {
                "type": "breathing_exercise",
                "display_name": "Breathing Exercise",
                "description": "Focused breathing patterns",
                "icon": "🌬️",
                "typical_duration": "60-300 seconds",
                "required_fields": ["title", "description"],
                "optional_fields": ["breathing_pattern"],
                "breathing_patterns": ["4-4-4-4", "4-7-8", "breath_of_fire", "4-4-6-2"]
            },
            {
                "type": "meditation",
                "display_name": "Meditation",
                "description": "Guided meditation session",
                "icon": "🧘‍♂️",
                "typical_duration": "180-900 seconds",
                "required_fields": ["title", "description"],
                "optional_fields": ["meditation_type", "meditation_voice", "meditation_background"],
                "meditation_types": ["breathing", "body_scan", "mindfulness", "focus"],
                "voice_options": ["calm_female", "calm_male", "energetic_female", "energetic_male"],
                "background_options": ["nature", "rain", "ocean", "birds", "silence"]
            },
            {
                "type": "spotify_playlist",
                "display_name": "Music/Playlist",
                "description": "Play Spotify music or playlists",
                "icon": "🎵",
                "typical_duration": "30-60 seconds",
                "required_fields": ["title", "description"],
                "optional_fields": ["spotify_playlist_id", "spotify_search_query"],
                "note": "Either playlist_id or search_query required"
            },
            {
                "type": "intention_setting",
                "display_name": "Intention Setting",
                "description": "Define goals and purpose",
                "icon": "🎯",
                "typical_duration": "60-180 seconds",
                "required_fields": ["title", "description"],
                "optional_fields": []
            },
            {
                "type": "custom_action",
                "display_name": "Custom Action",
                "description": "Any other custom activity",
                "icon": "⚙️",
                "typical_duration": "30-600 seconds",
                "required_fields": ["title", "description", "custom_instructions"],
                "optional_fields": []
            }
        ]
    }
