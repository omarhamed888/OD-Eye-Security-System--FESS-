import pytest
from src.cache.redis_cache import RedisCache
from unittest.mock import MagicMock, patch

@patch('redis.Redis')
def test_redis_cache_operations(mock_redis):
    """Test basic redis operations."""
    mock_instance = mock_redis.return_value
    mock_instance.ping.return_value = True
    
    cache = RedisCache()
    
    # Test set
    cache.set("key", "value")
    mock_instance.set.assert_called_once()
    
    # Test get
    import pickle
    mock_instance.get.return_value = pickle.dumps("value")
    assert cache.get("key") == "value"
    
    # Test delete
    cache.delete("key")
    mock_instance.delete.assert_called_once()
