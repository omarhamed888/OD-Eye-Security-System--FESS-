from typing import Optional, Dict, Any
import numpy as np
from datetime import datetime

from .redis_cache import RedisCache
from ..config.settings import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__, settings.log_level)

class FaceCache:
    """Distributed face encoding cache using Redis."""
    
    def __init__(self, redis_client: Optional[RedisCache] = None):
        """
        Initialize face cache.
        
        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client or RedisCache()
        self.ttl = settings.cache.face_ttl
        self.key_prefix = "face:"
    
    def cache_face(
        self,
        face_id: str,
        encoding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Cache a face encoding.
        
        Args:
            face_id: Unique face identifier
            encoding: Face encoding vector (numpy array)
            metadata: Optional metadata (name, last_seen, etc.)
            
        Returns:
            True if cached successfully
        """
        try:
            cache_data = {
                "encoding": encoding.tolist(),  # Convert numpy to list
                "metadata": metadata or {},
                "cached_at": datetime.utcnow().isoformat()
            }
            
            key = f"{self.key_prefix}{face_id}"
            success = self.redis.set(key, cache_data, ttl=self.ttl)
            
            if success:
                logger.debug(f"Cached face: {face_id}")
            else:
                logger.warning(f"Failed to cache face: {face_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error caching face {face_id}: {e}")
            return False
    
    def get_face(self, face_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached face encoding.
        
        Args:
            face_id: Face identifier
            
        Returns:
            Dict with encoding and metadata, or None
        """
        try:
            key = f"{self.key_prefix}{face_id}"
            cached = self.redis.get(key)
            
            if cached:
                # Convert encoding back to numpy array
                cached["encoding"] = np.array(cached["encoding"])
                logger.debug(f"Cache HIT: {face_id}")
                return cached
            else:
                logger.debug(f"Cache MISS: {face_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting face {face_id}: {e}")
            return None
    
    def delete_face(self, face_id: str) -> bool:
        """Delete a cached face."""
        key = f"{self.key_prefix}{face_id}"
        return self.redis.delete(key)
    
    def face_exists(self, face_id: str) -> bool:
        """Check if face is cached."""
        key = f"{self.key_prefix}{face_id}"
        return self.redis.exists(key)
