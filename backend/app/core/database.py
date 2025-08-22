from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Optimized database manager with connection pooling"""
    
    def __init__(self):
        self._client = None
        self._database = None
        self._initialized = False
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize with proper connection pooling"""
        if self._initialized:
            return
            
        async with self._lock:
            if self._initialized:
                return
                
            try:
                self._client = AsyncIOMotorClient(
                    settings.MONGODB_URI,
                    maxPoolSize=50,          # Max connections
                    minPoolSize=10,          # Min connections
                    maxIdleTimeMS=30000,     # 30s idle timeout
                    serverSelectionTimeoutMS=5000,  # 5s server selection
                    retryWrites=True,
                    w='majority'
                )
                self._database = self._client[settings.DATABASE_NAME]
                
                # Test connection
                await self._client.admin.command('ping')
                self._initialized = True
                logger.info("Successfully connected to MongoDB with connection pooling")
                
            except Exception as e:
                logger.error(f"Error connecting to MongoDB: {e}")
                raise
        
    @property
    def database(self):
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._database
        
    @property
    def client(self):
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._client
        
    async def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._initialized = False
            logger.info("MongoDB connection closed")
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            if not self._initialized:
                return False
            await self._client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global database manager
db_manager = DatabaseManager()

# Legacy Database class for compatibility
class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    """Get database instance with optimized connection pooling"""
    if not db_manager._initialized:
        await db_manager.initialize()
    return db_manager.database

async def connect_to_mongo():
    """Create database connection (legacy compatibility)"""
    await db_manager.initialize()
    # Update legacy db object for backward compatibility
    db.client = db_manager.client
    db.database = db_manager.database

async def close_mongo_connection():
    """Close database connection"""
    await db_manager.close()
    db.client = None
    db.database = None
    await db_manager.close()
        print("Disconnected from MongoDB")
