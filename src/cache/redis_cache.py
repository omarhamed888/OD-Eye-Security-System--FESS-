from typing import Optional, Any
import redis
from redis.connection import ConnectionPool
import pickle
import json

from ..config.settings import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__, settings.log_level)

class RedisCache:
    """Redis client wrapper with connection pooling."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
        max_connections: Optional[int] = None
    ):
        """
        Initialize Redis client with connection pool.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            max_connections: Max connections in pool
        """
        self.host = host or settings.redis.host
        self.port = port or settings.redis.port
        self.db = db or settings.redis.db
        self.password = password or settings.redis.password
        self.max_connections = max_connections or settings.redis.max_connections
        
        # Create connection pool
        self.pool = ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            max_connections=self.max_connections,
            socket_timeout=settings.redis.socket_timeout,
            decode_responses=False  # We'll handle encoding
        )
        
        self.client = redis.Redis(connection_pool=self.pool)
        
        # Test connection
        try:
            self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: str = "pickle"
    ) -> bool:
        """
        Set a key-value pair.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            serialize: Serialization method ('pickle' or 'json')
            
        Returns:
            True if successful
        """
        try:
            if serialize == "pickle":
                serialized = pickle.dumps(value)
            elif serialize == "json":
                serialized = json.dumps(value).encode('utf-8')
            else:
                raise ValueError(f"Unknown serialization: {serialize}")
            
            if ttl:
                return self.client.setex(key, ttl, serialized)
            else:
                return self.client.set(key, serialized)
                
        except Exception as e:
            logger.error(f"Redis SET failed for key '{key}': {e}")
            return False
    
    def get(
        self,
        key: str,
        deserialize: str = "pickle"
    ) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: Cache key
            deserialize: Deserialization method
            
        Returns:
            Cached value or None
        """
        try:
            value = self.client.get(key)
            
            if value is None:
                return None
            
            if deserialize == "pickle":
                return pickle.loads(value)
            elif deserialize == "json":
                return json.loads(value.decode('utf-8'))
            else:
                raise ValueError(f"Unknown deserialization: {deserialize}")
                
        except Exception as e:
            logger.error(f"Redis GET failed for key '{key}': {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key."""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE failed for key '{key}': {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS failed for key '{key}': {e}")
            return False
    
    def close(self) -> None:
        """Close the Redis connection."""
        try:
            self.client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
