"""
Distributed caching system using Redis with fallback to local cache.
Provides high-performance caching with automatic serialization and TTL management.
"""

from backend.app.core.config import settings
import redis.asyncio as redis
import json
import pickle
import asyncio
import logging
from typing import Any, Optional, Union, Dict
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib

logger = logging.getLogger(__name__)

class LocalCache:
    """Local in-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from local cache"""
        async with self._lock:
            if key in self._cache:
                value, expires_at = self._cache[key]
                
                # Check if expired
                if expires_at and datetime.now() > expires_at:
                    del self._cache[key]
                    return None
                
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                return value
            
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in local cache"""
        async with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
            
            # Remove oldest if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._cache.popitem(last=False)
            
            self._cache[key] = (value, expires_at)
            self._cache.move_to_end(key)
    
    async def delete(self, key: str):
        """Delete value from local cache"""
        async with self._lock:
            self._cache.pop(key, None)
    
    async def clear(self):
        """Clear all cached values"""
        async with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)

class DistributedCache:
    """Redis-based distributed cache with local cache fallback"""
    
    def __init__(self, redis_url: str = settings.REDIS_URL, db: int = 1, max_connections: int = 20):
        self.redis_url = redis_url
        self.db = db
        self.max_connections = max_connections
        self.redis_client = None
        self.local_cache = LocalCache()
        self._initialized = False
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize Redis connection"""
        if self._initialized:
            return
            
        async with self._lock:
            if self._initialized:
                return
                
            try:
                self.redis_client = redis.Redis(
                    host='redis-master',
                    port=6379, 
                    db=self.db,
                    decode_responses=False,  # For pickle support
                    max_connections=self.max_connections,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_keepalive_options={}
                )
                
                # Test connection
                await self.redis_client.ping()
                self._initialized = True
                logger.info(f"Distributed cache initialized (Redis DB {self.db})")
                
            except Exception as e:
                logger.warning(f"Redis not available, using local cache only: {e}")
                self.redis_client = None
    
    def _generate_key(self, key: str, prefix: str = "ff") -> str:
        """Generate a consistent cache key"""
        return f"{prefix}:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            # Try JSON first for simple types (faster)
            if isinstance(value, (str, int, float, bool, list, dict)):
                return json.dumps(value).encode('utf-8')
            else:
                # Fall back to pickle for complex objects
                return pickle.dumps(value)
        except Exception:
            # Final fallback to pickle
            return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    async def get(self, key: str, use_local: bool = True) -> Optional[Any]:
        """Get cached value with local cache fallback"""
        cache_key = self._generate_key(key)
        
        # Check local cache first (fastest)
        if use_local:
            local_value = await self.local_cache.get(cache_key)
            if local_value is not None:
                return local_value
        
        # Check Redis if available
        if self.redis_client:
            try:
                data = await self.redis_client.get(cache_key)
                if data:
                    value = self._deserialize_value(data)
                    
                    # Store in local cache for faster access
                    if use_local:
                        await self.local_cache.set(cache_key, value, ttl=300)  # 5 min local cache
                    
                    return value
            except Exception as e:
                logger.warning(f"Redis get failed for key {key}: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 1800, use_local: bool = True):
        """Set cached value with TTL"""
        cache_key = self._generate_key(key)
        
        # Store in local cache
        if use_local:
            await self.local_cache.set(cache_key, value, ttl=min(ttl, 300))  # Max 5 min local
        
        # Store in Redis if available
        if self.redis_client:
            try:
                data = self._serialize_value(value)
                if ttl > 0:
                    await self.redis_client.setex(cache_key, ttl, data)
                else:
                    await self.redis_client.set(cache_key, data)
            except Exception as e:
                logger.warning(f"Redis set failed for key {key}: {e}")
    
    async def delete(self, key: str):
        """Delete cached value"""
        cache_key = self._generate_key(key)
        
        # Delete from local cache
        await self.local_cache.delete(cache_key)
        
        # Delete from Redis if available
        if self.redis_client:
            try:
                await self.redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis delete failed for key {key}: {e}")
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        cache_key = self._generate_key(key)
        
        # Check local cache first
        if await self.local_cache.get(cache_key) is not None:
            return True
        
        # Check Redis if available
        if self.redis_client:
            try:
                return bool(await self.redis_client.exists(cache_key))
            except Exception as e:
                logger.warning(f"Redis exists check failed for key {key}: {e}")
        
        return False
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        if self.redis_client:
            try:
                pattern_key = self._generate_key(f"*{pattern}*")
                keys = await self.redis_client.keys(pattern_key)
                if keys:
                    await self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} keys matching pattern: {pattern}")
            except Exception as e:
                logger.warning(f"Redis clear pattern failed: {e}")
        
        # Clear local cache (simple approach - clear all)
        await self.local_cache.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'local_cache_size': self.local_cache.size(),
            'redis_available': self.redis_client is not None,
            'initialized': self._initialized
        }
        
        if self.redis_client:
            try:
                info = await self.redis_client.info('memory')
                stats.update({
                    'redis_memory_used': info.get('used_memory_human', 'unknown'),
                    'redis_memory_peak': info.get('used_memory_peak_human', 'unknown'),
                    'redis_connected_clients': info.get('connected_clients', 0)
                })
            except Exception as e:
                logger.warning(f"Could not get Redis stats: {e}")
        
        return stats
    
    async def health_check(self) -> bool:
        """Check cache health"""
        try:
            if self.redis_client:
                await self.redis_client.ping()
                return True
            return False  # Redis not available but local cache works
        except Exception:
            return False
    
    async def close(self):
        """Close cache connections"""
        if self.redis_client:
            await self.redis_client.close()
        await self.local_cache.clear()
        self._initialized = False
        logger.info("Distributed cache closed")

# Cache utilities
class CacheKey:
    """Utility class for generating consistent cache keys"""
    
    @staticmethod
    def user_data(user_id: str, data_type: str) -> str:
        """Generate cache key for user data"""
        return f"user:{user_id}:{data_type}"
    
    @staticmethod
    def chain_result(chain_name: str, user_id: str, inputs_hash: str) -> str:
        """Generate cache key for chain results"""
        return f"chain:{chain_name}:{user_id}:{inputs_hash}"
    
    @staticmethod
    def ai_request(request_type: str, inputs_hash: str) -> str:
        """Generate cache key for AI requests"""
        return f"ai:{request_type}:{inputs_hash}"
    
    @staticmethod
    def task_data(task_id: str, data_type: str) -> str:
        """Generate cache key for task data"""
        return f"task:{task_id}:{data_type}"
    
    @staticmethod
    def hash_inputs(inputs: Dict[str, Any]) -> str:
        """Generate hash for input dictionary"""
        sorted_items = sorted(inputs.items())
        input_str = json.dumps(sorted_items, sort_keys=True, default=str)
        return hashlib.md5(input_str.encode()).hexdigest()

# Global cache instance
distributed_cache = DistributedCache()

# Convenience decorators
def cached(ttl: int = 1800, key_func: Optional[callable] = None):
    """Decorator for caching function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                func_name = func.__name__
                args_hash = CacheKey.hash_inputs({'args': args, 'kwargs': kwargs})
                cache_key = f"func:{func_name}:{args_hash}"
            
            # Try to get from cache
            cached_result = await distributed_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await distributed_cache.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator

def cache_invalidate(*cache_keys: str):
    """Decorator for invalidating cache on function execution"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Invalidate specified cache keys
            for key in cache_keys:
                await distributed_cache.delete(key)
            
            return result
        return wrapper
    return decorator
