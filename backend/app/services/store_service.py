from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.schemas import StoreItem, UserProfile
from pymongo.errors import DuplicateKeyError
import logging

logger = logging.getLogger(__name__)

class StoreService:
    def __init__(self, db):
        self.db = db
        self.store_collection = db.store
        self.profile_collection = db.user_profiles
        self.transactions_collection = db.transactions
        self.rewards_collection = db.rewards  # Track active/consumed rewards
    
    async def get_store_items(self, category: Optional[str] = None) -> List[StoreItem]:
        """Get all store items, optionally filtered by category"""
        store_doc = await self.store_collection.find_one({"_id": "default"})
        
        if not store_doc:
            # Create comprehensive default store aligned with FocusForge
            default_items = {
                # Break & Rest Rewards
                "Quick Break (5m)": {
                    "cost": 10, 
                    "type": "break", 
                    "description": "5-minute mindful break",
                    "duration_minutes": 5,
                    "category": "rest"
                },
                "Coffee Break": {
                    "cost": 15, 
                    "type": "break", 
                    "description": "Enjoy a coffee or tea break",
                    "duration_minutes": 10,
                    "category": "rest"
                },
                "Power Nap (20m)": {
                    "cost": 35, 
                    "type": "rest", 
                    "description": "20-minute rejuvenating power nap",
                    "duration_minutes": 20,
                    "category": "rest"
                },
                "Extended Break (15m)": {
                    "cost": 25, 
                    "type": "break", 
                    "description": "15-minute break to stretch and refresh",
                    "duration_minutes": 15,
                    "category": "rest"
                },
                
                # Entertainment Rewards
                "Gaming Session (30m)": {
                    "cost": 60, 
                    "type": "entertainment", 
                    "description": "30 minutes of guilt-free gaming",
                    "duration_minutes": 30,
                    "category": "entertainment"
                },
                "Music Session": {
                    "cost": 12, 
                    "type": "entertainment", 
                    "description": "Listen to your favorite playlist",
                    "duration_minutes": 0,  # No time limit
                    "category": "entertainment",
                    "spotify_integration": True
                },
                "YouTube/TikTok Time (15m)": {
                    "cost": 30, 
                    "type": "entertainment", 
                    "description": "15 minutes of social media scrolling",
                    "duration_minutes": 15,
                    "category": "entertainment"
                },
                "Movie Night": {
                    "cost": 120, 
                    "type": "entertainment", 
                    "description": "Evening movie or series binge",
                    "duration_minutes": 120,
                    "category": "entertainment"
                },
                
                # Food & Treats
                "Snack Attack": {
                    "cost": 20, 
                    "type": "food", 
                    "description": "Treat yourself to a favorite snack",
                    "category": "food"
                },
                "Fancy Coffee": {
                    "cost": 40, 
                    "type": "food", 
                    "description": "Order that expensive coffee you love",
                    "category": "food"
                },
                "Dessert Reward": {
                    "cost": 35, 
                    "type": "food", 
                    "description": "Indulge in a sweet treat",
                    "category": "food"
                },
                
                # Social & Activities
                "Call a Friend": {
                    "cost": 25, 
                    "type": "social", 
                    "description": "Guilt-free social time with friends",
                    "category": "social"
                },
                "Walk Outside": {
                    "cost": 15, 
                    "type": "activity", 
                    "description": "Take a refreshing walk outdoors",
                    "duration_minutes": 20,
                    "category": "wellness"
                },
                "Creative Time": {
                    "cost": 45, 
                    "type": "activity", 
                    "description": "Work on a personal creative project",
                    "duration_minutes": 60,
                    "category": "wellness"
                },
                
                # Wellness & Self-care
                "Meditation Session": {
                    "cost": 20, 
                    "type": "wellness", 
                    "description": "10-minute mindfulness meditation",
                    "duration_minutes": 10,
                    "category": "wellness"
                },
                "Bubble Bath": {
                    "cost": 50, 
                    "type": "wellness", 
                    "description": "Relaxing bath with all the extras",
                    "duration_minutes": 30,
                    "category": "wellness"
                },
                
                # Productivity Boosters
                "Focus Music Premium": {
                    "cost": 8, 
                    "type": "productivity", 
                    "description": "Unlock premium focus playlists",
                    "category": "productivity",
                    "spotify_integration": True
                },
                "Workspace Upgrade": {
                    "cost": 80, 
                    "type": "productivity", 
                    "description": "Small upgrade for your workspace",
                    "category": "productivity"
                }
            }
            
            await self.store_collection.insert_one({
                "_id": "default",
                "items": default_items,
                "last_updated": datetime.now()
            })
            store_doc = {"items": default_items}
        
        items = []
        for name, details in store_doc["items"].items():
            # Filter by category if specified
            if category and details.get("category") != category:
                continue
                
            items.append(StoreItem(
                name=name,
                cost=details["cost"],
                type=details["type"],
                description=details.get("description", ""),
                **{k: v for k, v in details.items() if k not in ["cost", "type", "description"]}
            ))
        
        return items
    
    async def get_store_categories(self) -> List[str]:
        """Get all available store categories"""
        store_doc = await self.store_collection.find_one({"_id": "default"})
        
        if not store_doc:
            await self.get_store_items()  # Initialize default items
            store_doc = await self.store_collection.find_one({"_id": "default"})
        
        categories = set()
        for item in store_doc["items"].values():
            categories.add(item.get("category", "other"))
        
        return sorted(list(categories))
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile with enhanced tracking"""
        profile_doc = await self.profile_collection.find_one({"user_id": user_id})
        
        if not profile_doc:
            # Create default profile with FocusForge enhancements
            profile_doc = {
                "_id": f"profile_{user_id}",
                "user_id": user_id,
                "currency": 0,
                "total_earned": 0,  # Track lifetime earnings
                "total_spent": 0,   # Track lifetime spending
                "purchases": [],
                "active_rewards": [],  # Currently active/unused rewards
                "preferences": {
                    "favorite_categories": [],
                    "reward_notifications": True
                },
                "stats": {
                    "level": 1,
                    "tasks_completed": 0,
                    "pomodoros_completed": 0,
                    "streak_days": 0,
                    "last_activity": None
                },
                "created_at": datetime.now(),
                "last_updated": datetime.now()
            }
            await self.profile_collection.insert_one(profile_doc)
        
        profile_doc["_id"] = str(profile_doc["_id"])
        return UserProfile(**profile_doc)
    
    async def add_currency(self, user_id: str, amount: int, source: str = "task_completion", 
                          task_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """Add currency to user profile with transaction tracking"""
        try:
            # Record transaction
            transaction = {
                "user_id": user_id,
                "type": "earning",
                "amount": amount,
                "source": source,  # "task_completion", "bonus", "admin", etc.
                "task_id": task_id,
                "metadata": metadata or {},
                "timestamp": datetime.now()
            }
            await self.transactions_collection.insert_one(transaction)
            
            # Update profile
            result = await self.profile_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "currency": amount,
                        "total_earned": amount
                    },
                    "$set": {
                        "last_updated": datetime.now(),
                        "stats.last_activity": datetime.now()
                    },
                    "$setOnInsert": {
                        "_id": f"profile_{user_id}",
                        "user_id": user_id,
                        "total_spent": 0,
                        "purchases": [],
                        "active_rewards": [],
                        "preferences": {},
                        "stats": {
                            "level": 1,
                            "tasks_completed": 0,
                            "pomodoros_completed": 0,
                            "streak_days": 0
                        },
                        "created_at": datetime.now()
                    }
                },
                upsert=True
            )
            
            # Check for level up
            await self._check_level_up(user_id)
            
            return {"success": True, "new_balance": await self._get_user_currency(user_id)}
            
        except Exception as e:
            logger.error(f"Error adding currency for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def purchase_item(self, user_id: str, item_name: str) -> Dict[str, Any]:
        """Purchase an item from the store with enhanced tracking"""
        try:
            # Get store items
            store_doc = await self.store_collection.find_one({"_id": "default"})
            if not store_doc or item_name not in store_doc["items"]:
                return {"success": False, "message": "Item not found"}
            
            item = store_doc["items"][item_name]
            
            # Get user profile
            profile = await self.get_user_profile(user_id)
            
            if profile.currency < item["cost"]:
                return {
                    "success": False, 
                    "message": f"Not enough points. Need {item['cost']}, have {profile.currency}"
                }
            
            # Create reward record for time-based items
            reward_record = None
            if item.get("duration_minutes", 0) > 0:
                reward_record = {
                    "_id": f"reward_{user_id}_{datetime.now().timestamp()}",
                    "user_id": user_id,
                    "item_name": item_name,
                    "item_details": item,
                    "purchased_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(days=7),  # Rewards expire in 7 days
                    "used": False,
                    "used_at": None
                }
                await self.rewards_collection.insert_one(reward_record)
            
            # Record transaction
            transaction = {
                "user_id": user_id,
                "type": "purchase",
                "amount": -item["cost"],
                "item_name": item_name,
                "item_details": item,
                "reward_id": reward_record["_id"] if reward_record else None,
                "timestamp": datetime.now()
            }
            await self.transactions_collection.insert_one(transaction)
            
            # Update profile
            update_data = {
                "$inc": {
                    "currency": -item["cost"],
                    "total_spent": item["cost"]
                },
                "$push": {"purchases": item_name},
                "$set": {"last_updated": datetime.now()}
            }
            
            if reward_record:
                update_data["$push"]["active_rewards"] = reward_record["_id"]
            
            await self.profile_collection.update_one(
                {"user_id": user_id},
                update_data
            )
            
            return {
                "success": True,
                "message": f"Successfully purchased: {item_name}",
                "item": item,
                "new_balance": profile.currency - item["cost"],
                "reward_id": reward_record["_id"] if reward_record else None
            }
            
        except Exception as e:
            logger.error(f"Error purchasing item for user {user_id}: {e}")
            return {"success": False, "message": f"Purchase failed: {str(e)}"}
    
    async def get_active_rewards(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's active (unused) rewards"""
        try:
            rewards = await self.rewards_collection.find({
                "user_id": user_id,
                "used": False,
                "expires_at": {"$gt": datetime.now()}
            }).sort("purchased_at", -1).to_list(None)
            
            return rewards
            
        except Exception as e:
            logger.error(f"Error getting active rewards for user {user_id}: {e}")
            return []
    
    async def use_reward(self, user_id: str, reward_id: str) -> Dict[str, Any]:
        """Mark a reward as used"""
        try:
            result = await self.rewards_collection.update_one(
                {
                    "_id": reward_id,
                    "user_id": user_id,
                    "used": False
                },
                {
                    "$set": {
                        "used": True,
                        "used_at": datetime.now()
                    }
                }
            )
            
            if result.modified_count == 0:
                return {"success": False, "message": "Reward not found or already used"}
            
            # Remove from active rewards in profile
            await self.profile_collection.update_one(
                {"user_id": user_id},
                {"$pull": {"active_rewards": reward_id}}
            )
            
            reward = await self.rewards_collection.find_one({"_id": reward_id})
            
            return {
                "success": True,
                "message": f"Enjoy your {reward['item_name']}!",
                "reward": reward
            }
            
        except Exception as e:
            logger.error(f"Error using reward {reward_id} for user {user_id}: {e}")
            return {"success": False, "message": f"Failed to use reward: {str(e)}"}
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        try:
            profile = await self.get_user_profile(user_id)
            
            # Get transaction stats
            earnings = await self.transactions_collection.aggregate([
                {"$match": {"user_id": user_id, "type": "earning"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
            ]).to_list(None)
            
            purchases = await self.transactions_collection.aggregate([
                {"$match": {"user_id": user_id, "type": "purchase"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
            ]).to_list(None)
            
            # Get favorite categories
            favorite_categories = await self.transactions_collection.aggregate([
                {"$match": {"user_id": user_id, "type": "purchase"}},
                {"$lookup": {
                    "from": "store",
                    "localField": "item_details.category",
                    "foreignField": "items.category",
                    "as": "category_info"
                }},
                {"$group": {"_id": "$item_details.category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 3}
            ]).to_list(None)
            
            return {
                "profile": profile,
                "earnings": {
                    "total": earnings[0]["total"] if earnings else 0,
                    "count": earnings[0]["count"] if earnings else 0
                },
                "spending": {
                    "total": abs(purchases[0]["total"]) if purchases else 0,
                    "count": purchases[0]["count"] if purchases else 0
                },
                "favorite_categories": [cat["_id"] for cat in favorite_categories if cat["_id"]],
                "active_rewards_count": len(await self.get_active_rewards(user_id))
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            return {"error": str(e)}
    
    async def _check_level_up(self, user_id: str):
        """Check if user should level up based on total earnings"""
        profile = await self.profile_collection.find_one({"user_id": user_id})
        if not profile:
            return
        
        current_level = profile.get("stats", {}).get("level", 1)
        total_earned = profile.get("total_earned", 0)
        
        # Simple leveling formula: level = sqrt(total_earned / 100) + 1
        new_level = int((total_earned / 100) ** 0.5) + 1
        
        if new_level > current_level:
            await self.profile_collection.update_one(
                {"user_id": user_id},
                {"$set": {"stats.level": new_level}}
            )
            
            # Award level-up bonus
            bonus = new_level * 10
            await self.add_currency(user_id, bonus, "level_up", metadata={"new_level": new_level})
    
    async def _get_user_currency(self, user_id: str) -> int:
        """Helper to get current user currency"""
        profile = await self.profile_collection.find_one({"user_id": user_id})
        return profile.get("currency", 0) if profile else 0
    
    async def add_custom_store_item(self, item_name: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a custom item to the store (admin function)"""
        try:
            await self.store_collection.update_one(
                {"_id": "default"},
                {
                    "$set": {
                        f"items.{item_name}": item_data,
                        "last_updated": datetime.now()
                    }
                },
                upsert=True
            )
            
            return {"success": True, "message": f"Added item: {item_name}"}
            
        except Exception as e:
            logger.error(f"Error adding custom store item: {e}")
            return {"success": False, "message": f"Failed to add item: {str(e)}"}