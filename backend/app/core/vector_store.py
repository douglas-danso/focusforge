"""
Vector Store for Semantic Memory
Implements FAISS-based vector storage with OpenAI embeddings
"""

import asyncio
import logging
from typing import Any, Dict, List
from datetime import datetime, timedelta
import numpy as np
import faiss
from openai import OpenAI

from app.core.config import settings
from app.core.database import get_database

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-based vector store for semantic memory
    Provides similarity search and semantic indexing
    """
    
    def __init__(self):
        self.index = None
        self.dimension = 1536  # OpenAI text-embedding-ada-002 dimension
        self.vectors = []
        self.metadata = []
        self.openai_client = None
        self.db = None
        self.collection_name = "vector_store"
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the vector store"""
        if self.is_initialized:
            return
        
        try:
            # Initialize OpenAI client
            if settings.OPENAI_API_KEY:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized for vector store")
            else:
                logger.warning("OpenAI API key not found - vector store will use fallback methods")
            
            # Initialize database connection
            self.db = await get_database()
            
            # Initialize FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            
            # Load existing vectors from database
            await self._load_existing_vectors()
            
            self.is_initialized = True
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            # Create a minimal index as fallback
            self.index = faiss.IndexFlatIP(self.dimension)
            self.is_initialized = True
    
    async def _load_existing_vectors(self):
        """Load existing vectors from database"""
        try:
            collection = self.db[self.collection_name]
            cursor = collection.find({})
            
            vectors = []
            metadata_list = []
            
            async for doc in cursor:
                if "vector" in doc and "metadata" in doc:
                    vector = np.array(doc["vector"], dtype=np.float32)
                    vectors.append(vector)
                    metadata_list.append(doc["metadata"])
            
            if vectors:
                vectors_array = np.array(vectors, dtype=np.float32)
                self.index.add(vectors_array)
                self.vectors = vectors
                self.metadata = metadata_list
                logger.info(f"Loaded {len(vectors)} existing vectors")
            
        except Exception as e:
            logger.warning(f"Could not load existing vectors: {e}")
    
    async def add_text(self, text: str, metadata: Dict[str, Any], user_id: str = None) -> str:
        """Add text to vector store with metadata"""
        try:
            # Generate embedding
            if self.openai_client:
                embedding = await self._get_openai_embedding(text)
            else:
                # Fallback: simple hash-based vector
                embedding = self._get_fallback_embedding(text)
            
            # Add to FAISS index
            vector_array = np.array([embedding], dtype=np.float32)
            self.index.add(vector_array)
            
            # Store in memory
            self.vectors.append(embedding)
            self.metadata.append(metadata)
            
            # Store in database
            if self.db:
                doc_id = f"vec_{datetime.now().timestamp()}_{hash(text) % 10000}"
                await self.db[self.collection_name].insert_one({
                    "_id": doc_id,
                    "vector": embedding.tolist(),
                    "metadata": metadata,
                    "user_id": user_id,
                    "text": text,
                    "created_at": datetime.now()
                })
                return doc_id
            
            return f"local_{len(self.vectors)}"
            
        except Exception as e:
            logger.error(f"Failed to add text to vector store: {e}")
            return None
    
    async def _get_openai_embedding(self, text: str) -> np.ndarray:
        """Get OpenAI embedding for text"""
        try:
            response = await asyncio.to_thread(
                self.openai_client.embeddings.create,
                input=text,
                model="text-embedding-ada-002"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            return self._get_fallback_embedding(text)
    
    def _get_fallback_embedding(self, text: str) -> np.ndarray:
        """Generate fallback embedding using simple hash-based method"""
        # Simple hash-based vector generation
        import hashlib
        
        # Create a hash of the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to vector
        vector = np.zeros(self.dimension, dtype=np.float32)
        for i, char in enumerate(text_hash):
            if i < self.dimension:
                vector[i] = (ord(char) - ord('a')) / 26.0
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    async def search_similar(self, query: str, k: int = 5, 
                           user_id: str = None, 
                           metadata_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for similar texts"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Generate query embedding
            if self.openai_client:
                query_vector = await self._get_openai_embedding(query)
            else:
                query_vector = self._get_fallback_embedding(query)
            
            # Search in FAISS index
            query_array = np.array([query_vector], dtype=np.float32)
            scores, indices = self.index.search(query_array, min(k, len(self.vectors)))
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.metadata) and idx >= 0:
                    metadata = self.metadata[idx]
                    
                    # Apply user filter
                    if user_id and metadata.get("user_id") != user_id:
                        continue
                    
                                # Apply metadata filter
            if metadata_filter:
                if not all(metadata.get(k) == v 
                          for k, v in metadata_filter.items()):
                    continue
                    
                    results.append({
                        "score": float(score),
                        "metadata": metadata,
                        "index": int(idx)
                    })
            
            # Sort by score (higher is better for inner product)
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results[:k]
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def search_by_metadata(self, metadata_filter: Dict[str, Any], 
                                user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search by metadata criteria"""
        try:
            if not self.db:
                return []
            
            collection = self.db[self.collection_name]
            
            # Build query
            query = {"metadata": {"$elemMatch": {}}}
            for key, value in metadata_filter.items():
                query["metadata"][key] = value
            
            if user_id:
                query["user_id"] = user_id
            
            cursor = collection.find(query).limit(limit)
            results = []
            
            async for doc in cursor:
                results.append({
                    "id": doc["_id"],
                    "metadata": doc["metadata"],
                    "text": doc.get("text", ""),
                    "created_at": doc.get("created_at")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Metadata search failed: {e}")
            return []
    
    async def delete_by_metadata(self, metadata_filter: Dict[str, Any], user_id: str = None) -> int:
        """Delete vectors by metadata criteria"""
        try:
            if not self.db:
                return 0
            
            collection = self.db[self.collection_name]
            
            # Build query
            query = {}
            for key, value in metadata_filter.items():
                query[f"metadata.{key}"] = value
            
            if user_id:
                query["user_id"] = user_id
            
            result = await collection.delete_many(query)
            deleted_count = result.deleted_count
            
            # Rebuild index if vectors were deleted
            if deleted_count > 0:
                await self._rebuild_index()
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Delete by metadata failed: {e}")
            return 0
    
    async def _rebuild_index(self):
        """Rebuild FAISS index from database"""
        try:
            if not self.db:
                return
            
            # Clear current index
            self.index = faiss.IndexFlatIP(self.dimension)
            self.vectors = []
            self.metadata = []
            
            # Reload from database
            await self._load_existing_vectors()
            
            logger.info("FAISS index rebuilt successfully")
            
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            stats = {
                "total_vectors": len(self.vectors),
                "index_size": self.index.ntotal if self.index else 0,
                "dimension": self.dimension,
                "is_initialized": self.is_initialized,
                "openai_available": self.openai_client is not None
            }
            
            if self.db:
                collection = self.db[self.collection_name]
                stats["database_vectors"] = await collection.count_documents({})
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_vectors(self, older_than_days: int = 30):
        """Clean up old vectors"""
        try:
            if not self.db:
                return
            
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            collection = self.db[self.collection_name]
            
            result = await collection.delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} old vectors")
                await self._rebuild_index()
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Global vector store instance
vector_store = VectorStore()
