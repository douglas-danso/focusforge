from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models.schemas import UserCreate, UserUpdate, User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db):
        self.db = db
        self.collection = db.users
    
    def _hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = await self.collection.find_one({
            "$or": [
                {"email": user_data.email},
                {"username": user_data.username}
            ]
        })
        
        if existing_user:
            raise ValueError("User with this email or username already exists")
        
        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "hashed_password": self._hash_password(user_data.password),
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        # Remove password from response
        del user_dict["hashed_password"]
        return User(**user_dict)
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        try:
            user_doc = await self.collection.find_one(
                {"_id": ObjectId(user_id)},
                {"hashed_password": 0}  # Exclude password
            )
            if user_doc:
                user_doc["_id"] = str(user_doc["_id"])
                return User(**user_doc)
            return None
        except Exception:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get a user by email (including password for auth)"""
        user_doc = await self.collection.find_one({"email": email})
        if user_doc:
            user_doc["_id"] = str(user_doc["_id"])
            return user_doc
        return None
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update a user"""
        try:
            update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items() if v is not None}
            
            if "password" in update_data:
                update_data["hashed_password"] = self._hash_password(update_data["password"])
                del update_data["password"]
            
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=True,
                projection={"hashed_password": 0}  # Exclude password
            )
            
            if result:
                result["_id"] = str(result["_id"])
                return User(**result)
            return None
        except Exception:
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user_doc = await self.get_user_by_email(email)
        if not user_doc:
            return None
        
        if not self._verify_password(password, user_doc["hashed_password"]):
            return None
        
        # Remove password from response
        del user_doc["hashed_password"]
        return User(**user_doc)

    async def get_all_users(self, limit: int = 100) -> List[User]:
        """Get all users"""
        cursor = self.collection.find().limit(limit)
        users = []
        async for user_doc in cursor:
            user_doc["_id"] = str(user_doc["_id"])
            del user_doc["hashed_password"]
            users.append(User(**user_doc))
        return users
