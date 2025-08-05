from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import UserCreate, UserUpdate, User
from app.services.user_service import UserService
from app.core.database import get_database

router = APIRouter()

@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    db=Depends(get_database)
):
    """Create a new user"""
    try:
        user_service = UserService(db)
        user = await user_service.create_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    db=Depends(get_database)
):
    """Get a user by ID"""
    try:
        user_service = UserService(db)
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db=Depends(get_database)
):
    """Update a user"""
    try:
        user_service = UserService(db)
        user = await user_service.update_user(user_id, user_update)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
