from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import StoreItem, UserProfile
from app.services.store_service import StoreService
from app.core.database import get_database

router = APIRouter()

@router.get("/items", response_model=List[StoreItem])
async def get_store_items(
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get all store items"""
    try:
        store_service = StoreService(db)
        items = await store_service.get_store_items()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Get user profile with currency and purchases"""
    try:
        store_service = StoreService(db)
        profile = await store_service.get_user_profile(user_id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/purchase/{item_name}")
async def purchase_item(
    item_name: str,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Purchase an item from the store"""
    try:
        store_service = StoreService(db)
        result = await store_service.purchase_item(user_id, item_name)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-currency/{amount}")
async def add_currency(
    amount: int,
    user_id: str = "default",  # TODO: Get from auth
    db=Depends(get_database)
):
    """Add currency to user profile"""
    try:
        store_service = StoreService(db)
        await store_service.add_currency(user_id, amount)
        profile = await store_service.get_user_profile(user_id)
        return {"message": f"Added {amount} currency", "new_balance": profile.currency}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
