from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import PomodoroSessionCreate, PomodoroSession
from app.services.pomodoro_service import PomodoroService
from app.core.database import get_database
from app.core.auth import get_current_user_from_token

router = APIRouter()

@router.post("/start", response_model=PomodoroSession)
async def start_pomodoro_session(
    session_data: PomodoroSessionCreate,
    user_id: str = Depends(get_current_user_from_token),
    db=Depends(get_database)
):
    """Start a new Pomodoro session"""
    try:
        pomodoro_service = PomodoroService(db)
        session = await pomodoro_service.start_session(user_id, session_data)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{session_id}/complete")
async def complete_pomodoro_session(
    session_id: str,
    user_id: str = Depends(get_current_user_from_token),
    db=Depends(get_database)
):
    """Complete a Pomodoro session"""
    try:
        pomodoro_service = PomodoroService(db)
        session = await pomodoro_service.complete_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session completed successfully", "session": session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[PomodoroSession])
async def get_pomodoro_sessions(
    user_id: str = Depends(get_current_user_from_token),
    task_id: str = None,
    db=Depends(get_database)
):
    """Get Pomodoro sessions for a user"""
    try:
        pomodoro_service = PomodoroService(db)
        sessions = await pomodoro_service.get_user_sessions(user_id, task_id)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=PomodoroSession)
async def get_pomodoro_session(
    session_id: str,
    user_id: str = Depends(get_current_user_from_token),
    db=Depends(get_database)
):
    """Get a specific Pomodoro session"""
    try:
        pomodoro_service = PomodoroService(db)
        session = await pomodoro_service.get_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
