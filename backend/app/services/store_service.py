from typing import List, Dict, Any
from app.models.schemas import StoreItem, UserProfile

class StoreService:
    def __init__(self, db):
        self.db = db
        self.store_collection = db.store
        self.profile_collection = db.user_profiles
    
    async def get_store_items(self) -> List[StoreItem]:
        """Get all store items"""
        store_doc = await self.store_collection.find_one({"_id": "default"})
        
        if not store_doc:
            # Create default store
            default_items = {
                "Snack Break": {"cost": 20, "type": "break", "description": "Take a 15-minute snack break"},
                "Gaming Time (30m)": {"cost": 50, "type": "entertainment", "description": "30 minutes of gaming time"},
                "Nap Time (20m)": {"cost": 30, "type": "rest", "description": "20-minute power nap"},
                "Coffee Break": {"cost": 15, "type": "break", "description": "Enjoy a coffee break"},
                "Music Session": {"cost": 10, "type": "entertainment", "description": "Listen to your favorite playlist"}
            }
            
            await self.store_collection.insert_one({
                "_id": "default",
                "items": default_items
            })
            store_doc = {"items": default_items}
        
        items = []
        for name, details in store_doc["items"].items():
            items.append(StoreItem(
                name=name,
                cost=details["cost"],
                type=details["type"],
                description=details.get("description", "")
            ))
        
        return items
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile"""
        profile_doc = await self.profile_collection.find_one({"user_id": user_id})
        
        if not profile_doc:
            # Create default profile
            profile_doc = {
                "_id": f"profile_{user_id}",
                "user_id": user_id,
                "currency": 0,
                "purchases": [],
                "preferences": {}
            }
            await self.profile_collection.insert_one(profile_doc)
        
        profile_doc["_id"] = str(profile_doc["_id"])
        return UserProfile(**profile_doc)
    
    async def add_currency(self, user_id: str, amount: int):
        """Add currency to user profile"""
        await self.profile_collection.update_one(
            {"user_id": user_id},
            {
                "$inc": {"currency": amount},
                "$setOnInsert": {
                    "_id": f"profile_{user_id}",
                    "user_id": user_id,
                    "purchases": [],
                    "preferences": {}
                }
            },
            upsert=True
        )
    
    async def purchase_item(self, user_id: str, item_name: str) -> str:
        """Purchase an item from the store"""
        # Get store items
        store_doc = await self.store_collection.find_one({"_id": "default"})
        if not store_doc or item_name not in store_doc["items"]:
            return "Item not found"
        
        item = store_doc["items"][item_name]
        
        # Get user profile
        profile = await self.get_user_profile(user_id)
        
        if profile.currency < item["cost"]:
            return "Not enough points"
        
        # Update profile - deduct currency and add purchase
        await self.profile_collection.update_one(
            {"user_id": user_id},
            {
                "$inc": {"currency": -item["cost"]},
                "$push": {"purchases": item_name}
            }
        )
        
        return f"Successfully purchased: {item_name}"
