import pytest
import pickle
from unittest.mock import MagicMock, patch
from src.cache.redis_cache import RedisCache

@patch('redis.Redis')
def test_redis_cache_error_handling(mock_redis):
    """Test redis cache handles connection and operation errors."""
    mock_instance = mock_redis.return_value
    
    # 1. Connection Error in Init
    mock_instance.ping.side_effect = Exception("Conn Error")
    with pytest.raises(Exception):
        RedisCache()
        
    # 2. Get/Set errors
    mock_instance.ping.side_effect = None
    mock_instance.ping.return_value = True
    cache = RedisCache()
    
    mock_instance.get.side_effect = Exception("Get Error")
    assert cache.get("key") is None
    
    mock_instance.set.side_effect = Exception("Set Error")
    assert cache.set("key", "val") is False
    
    mock_instance.delete.side_effect = Exception("Del Error")
    assert cache.delete("key") is False

def test_redis_cache_bad_data():
    """Test redis handles unpickling errors."""
    with patch('redis.Redis') as mock_redis:
        mock_instance = mock_redis.return_value
        mock_instance.ping.return_value = True
        cache = RedisCache()
        
        # Corrupt pickle data
        mock_instance.get.return_value = b'not a pickle'
        assert cache.get("bad_key") is None
