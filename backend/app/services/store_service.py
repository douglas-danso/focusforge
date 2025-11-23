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
        self.rewards_collection = db.rewards
        
        # Cache for store items to reduce DB calls
        self._store_cache = None
        self._cache_expiry = None
    
    async def get_store_items(self, category: Optional[str] = None, 
                            user_id: Optional[str] = None) -> List[StoreItem]:
        """Get all store items, optionally filtered by category with personalization"""
        # Use cache if valid (expires after 1 hour)
        if (self._store_cache and self._cache_expiry and 
            datetime.now() < self._cache_expiry):
            store_doc = self._store_cache
        else:
            store_doc = await self.store_collection.find_one({"_id": "default"})
            if not store_doc:
                store_doc = await self._create_default_store()
            
            # Cache the result
            self._store_cache = store_doc
            self._cache_expiry = datetime.now() + timedelta(hours=1)
        
        items = []
        user_profile = None
        
        # Get user profile for personalization
        if user_id:
            user_profile = await self.get_user_profile(user_id)
        
        for name, details in store_doc["items"].items():
            # Filter by category if specified
            if category and details.get("category") != category:
                continue
            
            # Add personalization flags
            item_data = details.copy()
            if user_profile:
                item_data["affordable"] = user_profile.currency >= details["cost"]
                item_data["previously_purchased"] = name in user_profile.purchases
                
                # Mark as recommended based on user preferences
                fav_categories = user_profile.preferences.get("favorite_categories", [])
                item_data["recommended"] = details.get("category") in fav_categories
            
            items.append(StoreItem(
                name=name,
                cost=details["cost"],
                type=details["type"],
                description=details.get("description", ""),
                **{k: v for k, v in item_data.items() 
                   if k not in ["cost", "type", "description"]}
            ))
        
        # Sort items: affordable first, then by cost
        if user_profile:
            items.sort(key=lambda x: (
                not x.affordable if hasattr(x, 'affordable') else False,
                x.cost
            ))
        
        return items
    
    async def get_store_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all available store categories with metadata"""
        store_doc = await self.store_collection.find_one({"_id": "default"})
        
        if not store_doc:
            await self._create_default_store()
            store_doc = await self.store_collection.find_one({"_id": "default"})
        
        categories = {}
        for item_name, item in store_doc["items"].items():
            cat = item.get("category", "other")
            if cat not in categories:
                categories[cat] = {
                    "name": cat,
                    "items_count": 0,
                    "price_range": {"min": float('inf'), "max": 0},
                    "description": self._get_category_description(cat)
                }
            
            categories[cat]["items_count"] += 1
            categories[cat]["price_range"]["min"] = min(
                categories[cat]["price_range"]["min"], item["cost"]
            )
            categories[cat]["price_range"]["max"] = max(
                categories[cat]["price_range"]["max"], item["cost"]
            )
        
        # Fix infinite min values
        for cat in categories.values():
            if cat["price_range"]["min"] == float('inf'):
                cat["price_range"]["min"] = 0
        
        return categories
    
    def _get_category_description(self, category: str) -> str:
        """Get friendly description for categories"""
        descriptions = {
            "rest": "Take breaks and recharge your energy",
            "entertainment": "Fun activities to reward your hard work",
            "food": "Treats and snacks to fuel your productivity",
            "social": "Connect with friends and family",
            "wellness": "Self-care and mental health activities",
            "productivity": "Tools and upgrades to enhance focus"
        }
        return descriptions.get(category, "Miscellaneous rewards")
    
    async def _create_default_store(self) -> Dict[str, Any]:
        """Create the default store with enhanced items"""
        default_items = {
            # Break & Rest Rewards
            "Quick Break (5m)": {
                "cost": 10, 
                "type": "break", 
                "description": "5-minute mindful break to reset your focus",
                "duration_minutes": 5,
                "category": "rest",
                "icon": "⏰",
                "popularity": 95
            },
            "Coffee Break": {
                "cost": 15, 
                "type": "break", 
                "description": "Enjoy a warm drink and moment of calm",
                "duration_minutes": 10,
                "category": "rest",
                "icon": "☕",
                "popularity": 90
            },
            "Power Nap (20m)": {
                "cost": 35, 
                "type": "rest", 
                "description": "20-minute rejuvenating power nap",
                "duration_minutes": 20,
                "category": "rest",
                "icon": "😴",
                "popularity": 75
            },
            "Extended Break (15m)": {
                "cost": 25, 
                "type": "break", 
                "description": "15-minute break to stretch and refresh",
                "duration_minutes": 15,
                "category": "rest",
                "icon": "🧘",
                "popularity": 80
            },
            
            # Entertainment Rewards
            "Gaming Session (30m)": {
                "cost": 60, 
                "type": "entertainment", 
                "description": "30 minutes of guilt-free gaming",
                "duration_minutes": 30,
                "category": "entertainment",
                "icon": "🎮",
                "popularity": 85
            },
            "Music Session": {
                "cost": 12, 
                "type": "entertainment", 
                "description": "Listen to your favorite playlist",
                "duration_minutes": 0,
                "category": "entertainment",
                "spotify_integration": True,
                "icon": "🎵",
                "popularity": 95
            },
            "YouTube/TikTok Time (15m)": {
                "cost": 30, 
                "type": "entertainment", 
                "description": "15 minutes of social media scrolling",
                "duration_minutes": 15,
                "category": "entertainment",
                "icon": "📱",
                "popularity": 70
            },
            "Movie Night": {
                "cost": 120, 
                "type": "entertainment", 
                "description": "Evening movie or series binge",
                "duration_minutes": 120,
                "category": "entertainment",
                "icon": "🎬",
                "popularity": 60
            },
            
            # Food & Treats
            "Snack Attack": {
                "cost": 20, 
                "type": "food", 
                "description": "Treat yourself to a favorite snack",
                "category": "food",
                "icon": "🍿",
                "popularity": 90
            },
            "Fancy Coffee": {
                "cost": 40, 
                "type": "food", 
                "description": "Order that expensive coffee you love",
                "category": "food",
                "icon": "☕",
                "special": True,
                "popularity": 65
            },
            "Dessert Reward": {
                "cost": 35, 
                "type": "food", 
                "description": "Indulge in a sweet treat",
                "category": "food",
                "icon": "🍰",
                "popularity": 75
            },
            
            # Social & Activities
            "Call a Friend": {
                "cost": 25, 
                "type": "social", 
                "description": "Guilt-free social time with friends",
                "category": "social",
                "icon": "📞",
                "popularity": 60
            },
            "Walk Outside": {
                "cost": 15, 
                "type": "activity", 
                "description": "Take a refreshing walk outdoors",
                "duration_minutes": 20,
                "category": "wellness",
                "icon": "🚶",
                "popularity": 85
            },
            "Creative Time": {
                "cost": 45, 
                "type": "activity", 
                "description": "Work on a personal creative project",
                "duration_minutes": 60,
                "category": "wellness",
                "icon": "🎨",
                "popularity": 55
            },
            
            # Wellness & Self-care
            "Meditation Session": {
                "cost": 20, 
                "type": "wellness", 
                "description": "10-minute mindfulness meditation",
                "duration_minutes": 10,
                "category": "wellness",
                "icon": "🧘‍♀️",
                "popularity": 70
            },
            "Bubble Bath": {
                "cost": 50, 
                "type": "wellness", 
                "description": "Relaxing bath with all the extras",
                "duration_minutes": 30,
                "category": "wellness",
                "icon": "🛁",
                "popularity": 45
            },
            
            # Productivity Boosters
            "Focus Music Premium": {
                "cost": 8, 
                "type": "productivity", 
                "description": "Unlock premium focus playlists",
                "category": "productivity",
                "spotify_integration": True,
                "icon": "🎧",
                "popularity": 80
            },
            "Workspace Upgrade": {
                "cost": 80, 
                "type": "productivity", 
                "description": "Small upgrade for your workspace",
                "category": "productivity",
                "icon": "🖥️",
                "special": True,
                "popularity": 40
            }
        }
        
        store_doc = {
            "_id": "default",
            "items": default_items,
            "last_updated": datetime.now(),
            "version": "1.0"
        }
        
        await self.store_collection.insert_one(store_doc)
        return store_doc
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile with enhanced tracking and caching"""
        profile_doc = await self.profile_collection.find_one({"user_id": user_id})
        
        if not profile_doc:
            profile_doc = await self._create_default_profile(user_id)
        
        # Calculate dynamic stats
        profile_doc["calculated_stats"] = await self._calculate_user_stats(user_id)
        
        profile_doc["_id"] = str(profile_doc["_id"])
        return UserProfile(**profile_doc)
    
    async def _create_default_profile(self, user_id: str) -> Dict[str, Any]:
        """Create default user profile"""
        profile_doc = {
            "_id": f"profile_{user_id}",
            "user_id": user_id,
            "currency": 0,
            "total_earned": 0,
            "total_spent": 0,
            "purchases": [],
            "active_rewards": [],
            "preferences": {
                "favorite_categories": [],
                "reward_notifications": True,
                "auto_redeem": False
            },
            "stats": {
                "level": 1,
                "tasks_completed": 0,
                "pomodoros_completed": 0,
                "streak_days": 0,
                "last_activity": None,
                "best_category": None
            },
            "achievements": [],
            "created_at": datetime.now(),
            "last_updated": datetime.now()
        }
        await self.profile_collection.insert_one(profile_doc)
        return profile_doc
    
    async def _calculate_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Calculate dynamic user statistics"""
        # Get recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_transactions = await self.transactions_collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": week_ago}
        })
        
        # Calculate saving rate
        profile = await self.profile_collection.find_one({"user_id": user_id})
        if profile:
            total_earned = profile.get("total_earned", 0)
            total_spent = profile.get("total_spent", 0)
            saving_rate = ((total_earned - total_spent) / total_earned * 100) if total_earned > 0 else 0
        else:
            saving_rate = 0
        
        return {
            "recent_activity": recent_transactions,
            "saving_rate": round(saving_rate, 1),
            "efficiency_score": min(100, recent_transactions * 10)  # Simple efficiency metric
        }
    
    async def add_currency(self, user_id: str, amount: int, source: str = "task_completion", 
                          task_id: Optional[str] = None, metadata: Optional[Dict] = None,
                          bonus_multiplier: float = 1.0) -> Dict[str, Any]:
        """Enhanced currency addition with bonus system"""
        try:
            # Apply bonus multiplier for special events
            final_amount = int(amount * bonus_multiplier)
            
            # Record transaction
            transaction = {
                "user_id": user_id,
                "type": "earning",
                "amount": final_amount,
                "base_amount": amount,
                "bonus_multiplier": bonus_multiplier,
                "source": source,
                "task_id": task_id,
                "metadata": metadata or {},
                "timestamp": datetime.now()
            }
            await self.transactions_collection.insert_one(transaction)
            
            # Update profile with streak calculation
            profile = await self.profile_collection.find_one({"user_id": user_id})
            current_streak = await self._calculate_streak(user_id)
            
            # Streak bonus
            if current_streak >= 3:
                streak_bonus = min(current_streak * 2, 20)  # Max 20 bonus
                final_amount += streak_bonus
                
                # Record streak bonus transaction
                await self.transactions_collection.insert_one({
                    "user_id": user_id,
                    "type": "streak_bonus",
                    "amount": streak_bonus,
                    "source": "streak",
                    "metadata": {"streak_days": current_streak},
                    "timestamp": datetime.now()
                })
            
            # Update profile
            result = await self.profile_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "currency": final_amount,
                        "total_earned": final_amount
                    },
                    "$set": {
                        "last_updated": datetime.now(),
                        "stats.last_activity": datetime.now(),
                        "stats.streak_days": current_streak
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
                            "pomodoros_completed": 0
                        },
                        "achievements": [],
                        "created_at": datetime.now()
                    }
                },
                upsert=True
            )
            
            # Check for achievements and level up
            achievements = await self._check_achievements(user_id)
            level_up = await self._check_level_up(user_id)
            
            response = {
                "success": True, 
                "amount_earned": final_amount,
                "base_amount": amount,
                "bonus_amount": final_amount - amount,
                "new_balance": await self._get_user_currency(user_id),
                "streak_days": current_streak
            }
            
            if achievements:
                response["new_achievements"] = achievements
            if level_up:
                response["level_up"] = level_up
                
            return response
            
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            return {"error": str(e)}
    
    async def get_leaderboard(self, limit: int = 10, timeframe: str = "all_time") -> List[Dict[str, Any]]:
        """Get user leaderboard for motivation"""
        try:
            match_filter = {}
            if timeframe == "monthly":
                month_ago = datetime.now() - timedelta(days=30)
                match_filter["timestamp"] = {"$gte": month_ago}
            elif timeframe == "weekly":
                week_ago = datetime.now() - timedelta(days=7)
                match_filter["timestamp"] = {"$gte": week_ago}
            
            pipeline = [
                {"$match": {**match_filter, "type": "earning"}},
                {"$group": {
                    "_id": "$user_id",
                    "total_earned": {"$sum": "$amount"},
                    "tasks_completed": {"$sum": 1}
                }},
                {"$sort": {"total_earned": -1}},
                {"$limit": limit}
            ]
            
            leaderboard = await self.transactions_collection.aggregate(pipeline).to_list(None)
            
            # Anonymize user IDs for privacy
            for i, entry in enumerate(leaderboard):
                entry["rank"] = i + 1
                entry["user_display"] = f"User {entry['_id'][-4:]}"  # Show last 4 chars
                del entry["_id"]
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def get_spending_insights(self, user_id: str) -> Dict[str, Any]:
        """Get user spending insights and recommendations"""
        try:
            # Get spending by category
            spending_pipeline = [
                {"$match": {"user_id": user_id, "type": "purchase"}},
                {"$group": {
                    "_id": "$item_details.category",
                    "total_spent": {"$sum": {"$abs": "$amount"}},
                    "purchase_count": {"$sum": 1},
                    "items": {"$addToSet": "$item_name"}
                }},
                {"$sort": {"total_spent": -1}}
            ]
            
            category_spending = await self.transactions_collection.aggregate(spending_pipeline).to_list(None)
            
            # Calculate total spending
            total_spent = sum(cat["total_spent"] for cat in category_spending)
            
            # Add percentages
            for category in category_spending:
                category["percentage"] = (category["total_spent"] / total_spent * 100) if total_spent > 0 else 0
            
            # Get recent spending trend (last 7 days vs previous 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            two_weeks_ago = datetime.now() - timedelta(days=14)
            
            recent_spending = await self.transactions_collection.aggregate([
                {"$match": {"user_id": user_id, "type": "purchase"}},
                {"$group": {
                    "_id": {
                        "$cond": [
                            {"$gte": ["$timestamp", week_ago]},
                            "recent",
                            {"$cond": [
                                {"$gte": ["$timestamp", two_weeks_ago]},
                                "previous",
                                "older"
                            ]}
                        ]
                    },
                    "total": {"$sum": {"$abs": "$amount"}}
                }}
            ]).to_list(None)
            
            recent_dict = {item["_id"]: item["total"] for item in recent_spending}
            trend = "stable"
            if recent_dict.get("recent", 0) > recent_dict.get("previous", 0) * 1.2:
                trend = "increasing"
            elif recent_dict.get("recent", 0) < recent_dict.get("previous", 0) * 0.8:
                trend = "decreasing"
            
            # Generate recommendations
            recommendations = []
            if not category_spending:
                recommendations.append("Start treating yourself! You've earned some rewards.")
            elif len(category_spending) == 1:
                recommendations.append("Try exploring other reward categories for variety!")
            elif category_spending[0]["percentage"] > 60:
                recommendations.append(f"You love {category_spending[0]['_id']} rewards! Consider trying {category_spending[-1]['_id']} for balance.")
            
            profile = await self.get_user_profile(user_id)
            if profile.currency > 100:
                recommendations.append("You're saving up! Consider treating yourself to something special.")
            
            return {
                "category_breakdown": category_spending,
                "total_spent": total_spent,
                "spending_trend": trend,
                "trend_data": recent_dict,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error getting spending insights for user {user_id}: {e}")
            return {"error": str(e)}
    
    async def expire_old_rewards(self) -> Dict[str, int]:
        """Clean up expired rewards (run as scheduled task)"""
        try:
            # Find expired rewards
            expired_rewards = await self.rewards_collection.find({
                "used": False,
                "expires_at": {"$lte": datetime.now()}
            }).to_list(None)
            
            expired_count = len(expired_rewards)
            
            if expired_count > 0:
                # Remove from user profiles
                for reward in expired_rewards:
                    await self.profile_collection.update_one(
                        {"user_id": reward["user_id"]},
                        {"$pull": {"active_rewards": reward["_id"]}}
                    )
                
                # Mark as expired (don't delete for audit purposes)
                await self.rewards_collection.update_many(
                    {
                        "used": False,
                        "expires_at": {"$lte": datetime.now()}
                    },
                    {
                        "$set": {
                            "expired": True,
                            "expired_at": datetime.now()
                        }
                    }
                )
            
            return {"expired_rewards": expired_count}
            
        except Exception as e:
            logger.error(f"Error expiring old rewards: {e}")
            return {"error": str(e)}
    
    async def _check_level_up(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Enhanced level up system with rewards"""
        profile = await self.profile_collection.find_one({"user_id": user_id})
        if not profile:
            return None
        
        current_level = profile.get("stats", {}).get("level", 1)
        total_earned = profile.get("total_earned", 0)
        
        # Enhanced leveling formula with diminishing returns
        new_level = int((total_earned / 50) ** 0.6) + 1
        
        if new_level > current_level:
            # Level up rewards scale with level
            bonus = new_level * 15
            
            await self.profile_collection.update_one(
                {"user_id": user_id},
                {"$set": {"stats.level": new_level}}
            )
            
            # Award level-up bonus
            await self.add_currency(
                user_id, 
                bonus, 
                "level_up", 
                metadata={"new_level": new_level, "previous_level": current_level}
            )
            
            return {
                "new_level": new_level,
                "previous_level": current_level,
                "bonus_awarded": bonus
            }
        
        return None
    
    async def _get_user_currency(self, user_id: str) -> int:
        """Helper to get current user currency"""
        profile = await self.profile_collection.find_one({"user_id": user_id})
        return profile.get("currency", 0) if profile else 0
    
    async def add_custom_store_item(self, item_name: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a custom item to the store (admin function) with validation"""
        try:
            # Validate required fields
            required_fields = ["cost", "type", "description", "category"]
            for field in required_fields:
                if field not in item_data:
                    return {"success": False, "message": f"Missing required field: {field}"}
            
            # Validate cost is positive
            if item_data["cost"] <= 0:
                return {"success": False, "message": "Cost must be positive"}
            
            # Add metadata
            item_data.update({
                "added_at": datetime.now(),
                "custom": True,
                "popularity": 0
            })
            
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
            
            # Clear cache
            self._store_cache = None
            self._cache_expiry = None
            
            return {"success": True, "message": f"Added item: {item_name}"}
            
        except Exception as e:
            logger.error(f"Error adding custom store item: {e}")
            return {"success": False, "message": f"Failed to add item: {str(e)}"}
    
    async def update_store_item(self, item_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing store item"""
        try:
            # Validate item exists
            store_doc = await self.store_collection.find_one({"_id": "default"})
            if not store_doc or item_name not in store_doc["items"]:
                return {"success": False, "message": "Item not found"}
            
            # Prepare update
            update_fields = {}
            for key, value in updates.items():
                update_fields[f"items.{item_name}.{key}"] = value
            
            update_fields["last_updated"] = datetime.now()
            
            await self.store_collection.update_one(
                {"_id": "default"},
                {"$set": update_fields}
            )
            
            # Clear cache
            self._store_cache = None
            self._cache_expiry = None
            
            return {"success": True, "message": f"Updated item: {item_name}"}
            
        except Exception as e:
            logger.error(f"Error updating store item: {e}")
            return {"success": False, "message": f"Failed to update item: {str(e)}"}
    
    async def remove_store_item(self, item_name: str) -> Dict[str, Any]:
        """Remove an item from the store"""
        try:
            result = await self.store_collection.update_one(
                {"_id": "default"},
                {
                    "$unset": {f"items.{item_name}": ""},
                    "$set": {"last_updated": datetime.now()}
                }
            )
            
            if result.modified_count == 0:
                return {"success": False, "message": "Item not found"}
            
            # Clear cache
            self._store_cache = None
            self._cache_expiry = None
            
            return {"success": True, "message": f"Removed item: {item_name}"}
            
        except Exception as e:
            logger.error(f"Error removing store item: {e}")
            return {"success": False, "message": f"Failed to remove item: {str(e)}"}
    
    async def _calculate_streak(self, user_id: str) -> int:
        """Calculate current streak of consecutive active days"""
        # Get transactions from last 30 days, grouped by day
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "type": "earning",
                    "timestamp": {"$gte": thirty_days_ago}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$timestamp"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": -1}}
        ]
        
        daily_activity = await self.transactions_collection.aggregate(pipeline).to_list(None)
        
        if not daily_activity:
            return 0
        
        # Calculate consecutive days
        streak = 0
        current_date = datetime.now().date()
        
        for day_data in daily_activity:
            day = datetime.strptime(day_data["_id"], "%Y-%m-%d").date()
            expected_date = current_date - timedelta(days=streak)
            
            if day == expected_date:
                streak += 1
            else:
                break
        
        return streak
    
    async def _check_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Check for new achievements"""
        profile = await self.profile_collection.find_one({"user_id": user_id})
        if not profile:
            return []
        
        current_achievements = profile.get("achievements", [])
        new_achievements = []
        
        # Define achievement conditions
        achievements = [
            {
                "id": "first_purchase",
                "name": "First Reward",
                "description": "Made your first purchase",
                "condition": len(profile.get("purchases", [])) >= 1,
                "reward": 10
            },
            {
                "id": "big_spender",
                "name": "Big Spender",
                "description": "Spent 500+ tokens",
                "condition": profile.get("total_spent", 0) >= 500,
                "reward": 50
            },
            {
                "id": "week_streak",
                "name": "Week Warrior",
                "description": "Maintained 7-day streak",
                "condition": profile.get("stats", {}).get("streak_days", 0) >= 7,
                "reward": 25
            },
            {
                "id": "level_5",
                "name": "Level Master",
                "description": "Reached level 5",
                "condition": profile.get("stats", {}).get("level", 1) >= 5,
                "reward": 100
            }
        ]
        
        for achievement in achievements:
            if (achievement["id"] not in current_achievements and 
                achievement["condition"]):
                
                new_achievements.append(achievement)
                current_achievements.append(achievement["id"])
                
                # Award achievement reward
                await self.add_currency(
                    user_id, 
                    achievement["reward"], 
                    "achievement",
                    metadata={"achievement": achievement["name"]}
                )
        
        # Update profile with new achievements
        if new_achievements:
            await self.profile_collection.update_one(
                {"user_id": user_id},
                {"$set": {"achievements": current_achievements}}
            )
        
        return new_achievements
    
    async def purchase_item(self, user_id: str, item_name: str) -> Dict[str, Any]:
        """Enhanced purchase with better validation and feedback"""
        try:
            # Get store items
            store_doc = await self.store_collection.find_one({"_id": "default"})
            if not store_doc or item_name not in store_doc["items"]:
                return {
                    "success": False, 
                    "message": "Item not found",
                    "error_code": "ITEM_NOT_FOUND"
                }
            
            item = store_doc["items"][item_name]
            
            # Get user profile
            profile = await self.get_user_profile(user_id)
            
            if profile.currency < item["cost"]:
                return {
                    "success": False, 
                    "message": f"Not enough tokens. Need {item['cost']}, have {profile.currency}",
                    "error_code": "INSUFFICIENT_FUNDS",
                    "shortfall": item["cost"] - profile.currency
                }
            
            # Create reward record for time-based items
            reward_record = None
            if item.get("duration_minutes", 0) > 0 or item.get("type") in ["break", "rest", "entertainment"]:
                reward_record = {
                    "_id": f"reward_{user_id}_{int(datetime.now().timestamp())}",
                    "user_id": user_id,
                    "item_name": item_name,
                    "item_details": item,
                    "purchased_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(days=7),
                    "used": False,
                    "used_at": None,
                    "notification_sent": False
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
            
            # Update preferences (favorite categories)
            await self._update_user_preferences(user_id, item)
            
            return {
                "success": True,
                "message": f"Successfully purchased: {item_name}",
                "item": item,
                "new_balance": profile.currency - item["cost"],
                "reward_id": reward_record["_id"] if reward_record else None,
                "reward_expires": reward_record["expires_at"] if reward_record else None
            }
            
        except Exception as e:
            logger.error(f"Error purchasing item for user {user_id}: {e}")
            return {
                "success": False, 
                "message": f"Purchase failed: {str(e)}",
                "error_code": "SYSTEM_ERROR"
            }
    
    async def _update_user_preferences(self, user_id: str, item: Dict[str, Any]):
        """Update user preferences based on purchase history"""
        category = item.get("category")
        if not category:
            return
        
        # Get current preferences
        profile = await self.profile_collection.find_one({"user_id": user_id})
        preferences = profile.get("preferences", {})
        favorite_categories = preferences.get("favorite_categories", [])
        
        # Add category to favorites if not already there and user has purchased 3+ items from this category
        purchase_count = await self.transactions_collection.count_documents({
            "user_id": user_id,
            "type": "purchase",
            "item_details.category": category
        })
        
        if purchase_count >= 3 and category not in favorite_categories:
            favorite_categories.append(category)
            await self.profile_collection.update_one(
                {"user_id": user_id},
                {"$set": {"preferences.favorite_categories": favorite_categories}}
            )
    
    async def get_active_rewards(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's active rewards with expiry warnings"""
        try:
            rewards = await self.rewards_collection.find({
                "user_id": user_id,
                "used": False,
                "expires_at": {"$gt": datetime.now()}
            }).sort("purchased_at", -1).to_list(None)
            
            # Add expiry warnings
            for reward in rewards:
                expires_in = reward["expires_at"] - datetime.now()
                reward["expires_in_days"] = expires_in.days
                reward["expires_soon"] = expires_in.days <= 1
            
            return rewards
            
        except Exception as e:
            logger.error(f"Error getting active rewards for user {user_id}: {e}")
            return []
    
    async def use_reward(self, user_id: str, reward_id: str) -> Dict[str, Any]:
        """Enhanced reward usage with better tracking"""
        try:
            # Get reward details first
            reward = await self.rewards_collection.find_one({
                "_id": reward_id,
                "user_id": user_id,
                "used": False
            })
            
            if not reward:
                return {"success": False, "message": "Reward not found or already used"}
            
            # Check if expired
            if reward["expires_at"] <= datetime.now():
                return {"success": False, "message": "Reward has expired"}
            
            # Mark as used
            result = await self.rewards_collection.update_one(
                {"_id": reward_id},
                {
                    "$set": {
                        "used": True,
                        "used_at": datetime.now()
                    }
                }
            )
            
            # Remove from active rewards in profile
            await self.profile_collection.update_one(
                {"user_id": user_id},
                {"$pull": {"active_rewards": reward_id}}
            )
            
            # Record usage transaction
            await self.transactions_collection.insert_one({
                "user_id": user_id,
                "type": "reward_used",
                "amount": 0,
                "item_name": reward["item_name"],
                "reward_id": reward_id,
                "timestamp": datetime.now()
            })
            
            return {
                "success": True,
                "message": f"Enjoy your {reward['item_name']}! 🎉",
                "reward": reward,
                "duration_minutes": reward["item_details"].get("duration_minutes", 0)
            }
            
        except Exception as e:
            logger.error(f"Error using reward {reward_id} for user {user_id}: {e}")
            return {"success": False, "message": f"Failed to use reward: {str(e)}"}
    
    # ... (rest of the methods remain the same with minor enhancements)
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Enhanced user statistics"""
        try:
            profile = await self.get_user_profile(user_id)
            
            # Get comprehensive transaction stats
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            stats = await self.transactions_collection.aggregate([
                {"$match": {"user_id": user_id}},
                {
                    "$facet": {
                        "all_time_earnings": [
                            {"$match": {"type": "earning"}},
                            {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
                        ],
                        "recent_earnings": [
                            {"$match": {"type": "earning", "timestamp": {"$gte": thirty_days_ago}}},
                            {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
                        ],
                        "all_time_purchases": [
                            {"$match": {"type": "purchase"}},
                            {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
                        ],
                        "favorite_categories": [
                            {"$match": {"type": "purchase"}},
                            {"$group": {"_id": "$item_details.category", "count": {"$sum": 1}, "spent": {"$sum": {"$abs": "$amount"}}}},
                            {"$sort": {"count": -1}},
                            {"$limit": 3}
                        ]
                    }
                }
            ]).to_list(None)
            
            if stats:
                result = stats[0]
                return {
                    "profile": profile,
                    "all_time_earnings": {
                        "total": result["all_time_earnings"][0]["total"] if result["all_time_earnings"] else 0,
                        "count": result["all_time_earnings"][0]["count"] if result["all_time_earnings"] else 0
                    },
                    "recent_earnings": {
                        "total": result["recent_earnings"][0]["total"] if result["recent_earnings"] else 0,
                        "count": result["recent_earnings"][0]["count"] if result["recent_earnings"] else 0
                    },
                    "spending": {
                        "total": abs(result["all_time_purchases"][0]["total"]) if result["all_time_purchases"] else 0,
                        "count": result["all_time_purchases"][0]["count"] if result["all_time_purchases"] else 0
                    },
                    "favorite_categories": result["favorite_categories"],
                    "active_rewards_count": len(await self.get_active_rewards(user_id))
                }
            
            return {"error": "No statistics available"}
            
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            return {"error": str(e)}