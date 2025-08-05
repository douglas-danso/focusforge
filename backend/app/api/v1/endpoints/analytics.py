from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import AnalyticsResponse
from app.services.analytics_service import AnalyticsService
from app.core.database import get_database

router = APIRouter()

@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get comprehensive analytics for a user"""
    try:
        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_user_analytics(user_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/streak")
async def get_streak(
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get current streak for a user"""
    try:
        analytics_service = AnalyticsService(db)
        streak = await analytics_service.get_streak(user_id)
        return {"current_streak": streak}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly")
async def get_weekly_stats(
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get weekly statistics"""
    try:
        analytics_service = AnalyticsService(db)
        stats = await analytics_service.get_weekly_stats(user_id)
        return {"weekly_stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly")
async def get_monthly_stats(
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get monthly statistics"""
    try:
        analytics_service = AnalyticsService(db)
        stats = await analytics_service.get_monthly_stats(user_id)
        return {"monthly_stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
