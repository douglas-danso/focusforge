"""
Memory layer for Memory-Chain-Planner architecture
Implements LangChain-compatible memory interfaces with MongoDB persistence
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_core.messages.utils import get_buffer_string


from app.core.database import get_database
from app.core.config import settings
from app.core.vector_store import vector_store

logger = logging.getLogger(__name__)


class MemoryType:
    """Memory type constants"""
    SHORT_TERM = "short_term"
    WORKING = "working"
    LONG_TERM = "long_term"
    SEMANTIC = "semantic"


class MemoryStore:
    """
    Centralized memory store with multiple memory types
    Compatible with LangChain memory interfaces
    """
    
    def __init__(self):
        self.db = None
        self.memory_collections = {
            MemoryType.SHORT_TERM: "memory_short_term",
            MemoryType.WORKING: "memory_working", 
            MemoryType.LONG_TERM: "memory_long_term",
            MemoryType.SEMANTIC: "memory_semantic"
        }
        self.memory_configs = {
            MemoryType.SHORT_TERM: {"ttl_seconds": 3600, "max_entries": 1000},
            MemoryType.WORKING: {"ttl_seconds": 86400, "max_entries": 500},
            MemoryType.LONG_TERM: {"ttl_seconds": None, "max_entries": 10000},
            MemoryType.SEMANTIC: {"ttl_seconds": None, "max_entries": 5000}
        }
    
    async def initialize(self):
        """Initialize memory store"""
        if self.db is None:
            self.db = await get_database()
            logger.info("Memory store initialized")
    
    async def store_memory(self, memory_type: str, key: str, value: Any, 
                          user_id: str = None, metadata: Dict = None) -> str:
        """Store memory entry"""
        await self.initialize()
        
        memory_entry = {
            "key": key,
            "value": value,
            "user_id": user_id,
            "metadata": metadata or {},
            "created_at": datetime.now(),
            "accessed_at": datetime.now(),
            "access_count": 1
        }
        
        # Add TTL if configured
        config = self.memory_configs.get(memory_type, {})
        if config.get("ttl_seconds"):
            memory_entry["expires_at"] = datetime.now() + timedelta(seconds=config["ttl_seconds"])
        
        collection_name = self.memory_collections[memory_type]
        collection = self.db[collection_name]
        
        # Upsert the memory entry
        result = await collection.replace_one(
            {"key": key, "user_id": user_id},
            memory_entry,
            upsert=True
        )
        
        # Cleanup old entries if needed
        await self._cleanup_memory(memory_type)
        
        return str(result.upserted_id or memory_entry.get("_id"))
    
    async def retrieve_memory(self, memory_type: str, key: str, user_id: str = None) -> Optional[Any]:
        """Retrieve memory entry"""
        await self.initialize()
        
        collection_name = self.memory_collections[memory_type]
        collection = self.db[collection_name]
        
        memory_entry = await collection.find_one({
            "key": key,
            "user_id": user_id,
            "$or": [
                {"expires_at": {"$exists": False}},
                {"expires_at": {"$gte": datetime.now()}}
            ]
        })
        
        if memory_entry:
            # Update access tracking
            await collection.update_one(
                {"_id": memory_entry["_id"]},
                {
                    "$set": {"accessed_at": datetime.now()},
                    "$inc": {"access_count": 1}
                }
            )
            return memory_entry["value"]
        
        return None
    
    async def search_memories(self, memory_type: str, query: Dict, 
                             user_id: str = None, limit: int = 10) -> List[Dict]:
        """Search memories with query"""
        await self.initialize()
        
        collection_name = self.memory_collections[memory_type]
        collection = self.db[collection_name]
        
        search_query = {**query}
        if user_id:
            search_query["user_id"] = user_id
        
        # Filter out expired entries
        search_query["$or"] = [
            {"expires_at": {"$exists": False}},
            {"expires_at": {"$gte": datetime.now()}}
        ]
        
        cursor = collection.find(search_query).sort("accessed_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def delete_memory(self, memory_type: str, key: str, user_id: str = None) -> bool:
        """Delete memory entry"""
        await self.initialize()
        
        collection_name = self.memory_collections[memory_type]
        collection = self.db[collection_name]
        
        result = await collection.delete_one({"key": key, "user_id": user_id})
        return result.deleted_count > 0
    
    async def _cleanup_memory(self, memory_type: str):
        """Cleanup expired and excess memory entries"""
        await self.initialize()
        
        collection_name = self.memory_collections[memory_type]
        collection = self.db[collection_name]
        config = self.memory_configs.get(memory_type, {})
        
        # Remove expired entries
        if config.get("ttl_seconds"):
            await collection.delete_many({
                "expires_at": {"$lt": datetime.now()}
            })
        
        # Remove excess entries if max_entries is set
        max_entries = config.get("max_entries")
        if max_entries:
            total_count = await collection.count_documents({})
            if total_count > max_entries:
                # Remove oldest entries beyond limit
                excess_entries = total_count - max_entries
                oldest_entries = await collection.find().sort("accessed_at", 1).limit(excess_entries).to_list(length=excess_entries)
                if oldest_entries:
                    ids_to_delete = [entry["_id"] for entry in oldest_entries]
                    await collection.delete_many({"_id": {"$in": ids_to_delete}})


class PersistentConversationMemory(ConversationBufferMemory):
    """
    LangChain-compatible conversation memory with MongoDB persistence
    """
    
    def __init__(self, memory_store: MemoryStore, user_id: str, session_id: str = "default", 
                 memory_key: str = "history", return_messages: bool = True):
        super().__init__()
        self.memory_store = memory_store
        self.user_id = user_id
        self.session_id = session_id
        self.memory_key = memory_key
        self.return_messages = return_messages
        self._buffer = []
        self._loaded = False
    
    @property
    def memory_variables(self) -> List[str]:
        """Return memory variables"""
        return [self.memory_key]
    
    async def _load_memory(self):
        """Load conversation history from memory store"""
        if self._loaded:
            return
        
        stored_messages = await self.memory_store.retrieve_memory(
            MemoryType.WORKING,
            f"conversation:{self.session_id}",
            self.user_id
        )
        
        if stored_messages:
            self._buffer = [self._deserialize_message(msg) for msg in stored_messages]
        
        self._loaded = True
    
    async def _save_memory(self):
        """Save conversation history to memory store"""
        serialized_messages = [self._serialize_message(msg) for msg in self._buffer]
        await self.memory_store.store_memory(
            MemoryType.WORKING,
            f"conversation:{self.session_id}",
            serialized_messages,
            self.user_id
        )
    
    def _serialize_message(self, message: BaseMessage) -> Dict:
        """Serialize LangChain message"""
        return {
            "type": message.__class__.__name__,
            "content": message.content,
            "additional_kwargs": getattr(message, "additional_kwargs", {}),
            "timestamp": datetime.now().isoformat()
        }
    
    def _deserialize_message(self, data: Dict) -> BaseMessage:
        """Deserialize message data"""
        if data["type"] == "HumanMessage":
            return HumanMessage(content=data["content"], additional_kwargs=data.get("additional_kwargs", {}))
        elif data["type"] == "AIMessage":
            return AIMessage(content=data["content"], additional_kwargs=data.get("additional_kwargs", {}))
        else:
            # Default to HumanMessage for unknown types
            return HumanMessage(content=data["content"])
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables synchronously (for LangChain compatibility)"""
        # Note: This is synchronous for LangChain compatibility
        # In practice, memory should be pre-loaded
        if self.return_messages:
            return {self.memory_key: self._buffer}
        else:
            return {self.memory_key: get_buffer_string(self._buffer)}
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context to memory"""
        input_str = inputs.get("input", "")
        output_str = outputs.get("output", "")
        
        self._buffer.append(HumanMessage(content=input_str))
        self._buffer.append(AIMessage(content=output_str))
        
        # Async save (will be handled by background task)
        asyncio.create_task(self._save_memory())
    
    def clear(self) -> None:
        """Clear the memory"""
        self._buffer = []
        asyncio.create_task(self.memory_store.delete_memory(
            MemoryType.WORKING,
            f"conversation:{self.session_id}",
            self.user_id
        ))


class MemoryManager:
    """
    High-level memory management interface
    Provides convenient access to different memory types
    """
    
    def __init__(self):
        self.memory_store = MemoryStore()
    
    async def initialize(self):
        """Initialize memory manager"""
        await self.memory_store.initialize()
    
    async def get_conversation_memory(self, user_id: str, session_id: str = "default") -> PersistentConversationMemory:
        """Get conversation memory for user session"""
        memory = PersistentConversationMemory(self.memory_store, user_id, session_id)
        await memory._load_memory()
        return memory
    
    async def store_user_context(self, user_id: str, context: Dict[str, Any]):
        """Store user context in long-term memory"""
        await self.memory_store.store_memory(
            MemoryType.LONG_TERM,
            f"user_context:{user_id}",
            context,
            user_id
        )
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user context from long-term memory"""
        context = await self.memory_store.retrieve_memory(
            MemoryType.LONG_TERM,
            f"user_context:{user_id}",
            user_id
        )
        return context or {}
    
    async def store_task_insights(self, user_id: str, task_id: str, insights: Dict[str, Any]):
        """Store task-related insights"""
        await self.memory_store.store_memory(
            MemoryType.LONG_TERM,
            f"task_insights:{task_id}",
            insights,
            user_id
        )
    
    async def get_task_insights(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """Retrieve task insights"""
        insights = await self.memory_store.retrieve_memory(
            MemoryType.LONG_TERM,
            f"task_insights:{task_id}",
            user_id
        )
        return insights or {}
    
    async def search_similar_tasks(self, user_id: str, task_description: str, limit: int = 5) -> List[Dict]:
        """Search for similar past tasks using semantic search"""
        try:
            # Use vector store for semantic search
            similar_results = await vector_store.search_similar(
                query=task_description,
                k=limit,
                user_id=user_id,
                metadata_filter={"type": "task_insights"}
            )
            
            # Convert to expected format
            results = []
            for result in similar_results:
                results.append({
                    "key": f"semantic_search_{result['index']}",
                    "value": result["metadata"],
                    "score": result["score"]
                })
            
            # Fallback to text-based search if vector search fails
            if not results:
                query = {
                    "key": {"$regex": "task_insights:.*", "$options": "i"},
                    "value.description": {"$regex": task_description, "$options": "i"}
                }
                results = await self.memory_store.search_memories(
                    MemoryType.LONG_TERM, query, user_id, limit
                )
            
            return results
            
        except Exception as e:
            logger.warning(f"Semantic search failed, falling back to text search: {e}")
            # Fallback to text-based search
            query = {
                "key": {"$regex": "task_insights:.*", "$options": "i"},
                "value.description": {"$regex": task_description, "$options": "i"}
            }
            return await self.memory_store.search_memories(
                MemoryType.LONG_TERM, query, user_id, limit
            )
    
    async def cleanup_all_memories(self):
        """Run cleanup on all memory types"""
        for memory_type in self.memory_store.memory_collections.keys():
            await self.memory_store._cleanup_memory(memory_type)


# Global memory manager instance
memory_manager = MemoryManager()
