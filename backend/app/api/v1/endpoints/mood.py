from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import MoodLogCreate, MoodLog
from app.services.mood_service import MoodService
from app.core.database import get_database

router = APIRouter()

@router.post("/", response_model=MoodLog)
async def log_mood(
    mood_data: MoodLogCreate,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Log a mood entry"""
    try:
        mood_service = MoodService(db)
        mood_log = await mood_service.log_mood(user_id, mood_data)
        return mood_log
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[MoodLog])
async def get_mood_logs(
    user_id: str = "default",  # TODO: Get from auth
    limit: int = 100,
    db=Depends(get_database)
):
    """Get mood logs for a user"""
    try:
        mood_service = MoodService(db)
        mood_logs = await mood_service.get_user_mood_logs(user_id, limit)
        return mood_logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_mood_trends(
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get mood trends for a user"""
    try:
        mood_service = MoodService(db)
        trends = await mood_service.get_mood_trends(user_id)
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/today")
async def reset_today_mood_logs(
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Reset today's mood logs"""
    try:
        mood_service = MoodService(db)
        deleted_count = await mood_service.reset_today_logs(user_id)
        return {"message": f"Deleted {deleted_count} mood logs for today"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
