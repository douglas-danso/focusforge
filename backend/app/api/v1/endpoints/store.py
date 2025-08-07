from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.models.schemas import StoreItem, UserProfile
from app.services.store_service import StoreService
from app.core.database import get_database

router = APIRouter()

# Request/Response models
class PurchaseResponse(BaseModel):
    success: bool
    message: str
    item: Optional[Dict[str, Any]] = None
    new_balance: Optional[int] = None
    reward_id: Optional[str] = None
    reward_expires: Optional[str] = None
    error_code: Optional[str] = None
    shortfall: Optional[int] = None

class CurrencyResponse(BaseModel):
    success: bool
    amount_earned: Optional[int] = None
    base_amount: Optional[int] = None
    bonus_amount: Optional[int] = None
    new_balance: int
    streak_days: Optional[int] = None
    new_achievements: Optional[List[Dict[str, Any]]] = None
    level_up: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CustomItemRequest(BaseModel):
    cost: int
    type: str
    description: str
    category: str
    duration_minutes: Optional[int] = 0
    icon: Optional[str] = "🎁"
    special: Optional[bool] = False

# Store Items Endpoints
@router.get("/items", response_model=List[StoreItem])
async def get_store_items(
    category: Optional[str] = Query(None, description="Filter by category"),
    user_id: str = Query("default", description="User ID for personalization"),
    db=Depends(get_database)
):
    """Get store items with optional filtering and personalization"""
    try:
        store_service = StoreService(db)
        items = await store_service.get_store_items(category=category, user_id=user_id)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch store items: {str(e)}")

@router.get("/categories")
async def get_store_categories(db=Depends(get_database)):
    """Get all store categories with metadata"""
    try:
        store_service = StoreService(db)
        categories = await store_service.get_store_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")

# User Profile & Currency Endpoints
@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    user_id: str = Query("default", description="User ID"),
    db=Depends(get_database)
):
    """Get user profile with currency, purchases, and stats"""
    try:
        store_service = StoreService(db)
        profile = await store_service.get_user_profile(user_id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user profile: {str(e)}")

@router.post("/currency/add", response_model=CurrencyResponse)
async def add_currency(
    amount: int = Query(..., ge=1, description="Amount to add"),
    source: str = Query("manual", description="Source of currency"),
    task_id: Optional[str] = Query(None, description="Associated task ID"),
    bonus_multiplier: float = Query(1.0, ge=0.1, le=5.0, description="Bonus multiplier"),
    user_id: str = Query("default", description="User ID"),
    db=Depends(get_database)
):
    """Add currency to user profile with bonus system"""
    try:
        store_service = StoreService(db)
        result = await store_service.add_currency(
            user_id=user_id,
            amount=amount,
            source=source,
            task_id=task_id,
            bonus_multiplier=bonus_multiplier
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to add currency"))
        
        return CurrencyResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add currency: {str(e)}")

# Purchase & Rewards Endpoints
@router.post("/purchase/{item_name}", response_model=PurchaseResponse)
async def purchase_item(
    item_name: str,
    user_id: str = Query("default", description="User ID"),
    db=Depends(get_database)
):
    """Purchase an item from the store"""
    try:
        store_service = StoreService(db)
        result = await store_service.purchase_item(user_id, item_name)
        
        if not result["success"]:
            status_code = 400
            if result.get("error_code") == "ITEM_NOT_FOUND":
                status_code = 404
            elif result.get("error_code") == "INSUFFICIENT_FUNDS":
                status_code = 402  # Payment Required
            
            raise HTTPException(status_code=status_code, detail=result["message"])
        
        return PurchaseResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")

@router.get("/rewards/active")
async def get_active_rewards(
    user_id: str = Query("default", description="User ID"),
    db=Depends(get_database)
):
    """Get user's active (unused) rewards"""
    try:
        store_service = StoreService(db)
        rewards = await store_service.get_active_rewards(user_id)
        return {
            "rewards": rewards,
            "count": len(rewards),
            "expiring_soon": [r for r in rewards if r.get("expires_soon", False)]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch active rewards: {str(e)}")

@router.post("/rewards/{reward_id}/use")
async def use_reward(
    reward_id: str,
    user_id: str = Query("default", description="User ID"),
    db=Depends(get_database)
):
    """Use/consume a reward"""
    try:
        store_service = StoreService(db)
        result = await store_service.use_reward(user_id, reward_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to use reward: {str(e)}")

# Statistics & Analytics Endpoints
@router.get("/stats")
async def get_user_stats(
    user_id: str = Query("default", description="User ID"),
    db=Depends(get_database)
):
    """Get comprehensive user statistics"""
    try:
        store_service = StoreService(db)
        stats = await store_service.get_user_stats(user_id)
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user stats: {str(e)}")

@router.get("/insights/spending")
async def get_spending_insights(
    user_id: str = Query("default", description="User ID"),
    db=Depends(get_database)
):
    """Get user spending insights and recommendations"""
    try:
        store_service = StoreService(db)
        insights = await store_service.get_spending_insights(user_id)
        
        if "error" in insights:
            raise HTTPException(status_code=500, detail=insights["error"])
        
        return insights
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch spending insights: {str(e)}")

@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=50, description="Number of users to return"),
    timeframe: str = Query("all_time", description="Timeframe: all_time, monthly, weekly"),
    db=Depends(get_database)
):
    """Get user leaderboard for motivation"""
    try:
        if timeframe not in ["all_time", "monthly", "weekly"]:
            raise HTTPException(status_code=400, detail="Invalid timeframe")
        
        store_service = StoreService(db)
        leaderboard = await store_service.get_leaderboard(limit=limit, timeframe=timeframe)
        
        return {
            "timeframe": timeframe,
            "leaderboard": leaderboard,
            "total_users": len(leaderboard)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch leaderboard: {str(e)}")

# Admin Endpoints
@router.post("/admin/items", dependencies=[])  # Add admin auth dependency
async def add_custom_item(
    item_name: str,
    item_data: CustomItemRequest,
    db=Depends(get_database)
):
    """Add a custom item to the store (admin only)"""
    try:
        store_service = StoreService(db)
        result = await store_service.add_custom_store_item(
            item_name, 
            item_data.dict()
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add custom item: {str(e)}")

@router.put("/admin/items/{item_name}", dependencies=[])  # Add admin auth dependency
async def update_store_item(
    item_name: str,
    updates: Dict[str, Any],
    db=Depends(get_database)
):
    """Update an existing store item (admin only)"""
    try:
        store_service = StoreService(db)
        result = await store_service.update_store_item(item_name, updates)
        
        if not result["success"]:
            status_code = 404 if "not found" in result["message"].lower() else 400
            raise HTTPException(status_code=status_code, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update item: {str(e)}")

@router.delete("/admin/items/{item_name}", dependencies=[])  # Add admin auth dependency
async def remove_store_item(
    item_name: str,
    db=Depends(get_database)
):
    """Remove an item from the store (admin only)"""
    try:
        store_service = StoreService(db)
        result = await store_service.remove_store_item(item_name)
        
        if not result["success"]:
            status_code = 404 if "not found" in result["message"].lower() else 400
            raise HTTPException(status_code=status_code, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove item: {str(e)}")

@router.post("/admin/cleanup/rewards", dependencies=[])  # Add admin auth dependency
async def expire_old_rewards(db=Depends(get_database)):
    """Clean up expired rewards (admin maintenance)"""
    try:
        store_service = StoreService(db)
        result = await store_service.expire_old_rewards()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "message": f"Cleaned up {result['expired_rewards']} expired rewards",
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clean up rewards: {str(e)}")

# Health & Utility Endpoints
@router.get("/health")
async def health_check(db=Depends(get_database)):
    """Health check endpoint"""
    try:
        store_service = StoreService(db)
        
        # Quick DB connectivity test
        await store_service.store_collection.find_one({"_id": "default"})
        
        return {
            "status": "healthy",
            "service": "store_service",
            "timestamp": store_service.db.client.server_info()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")