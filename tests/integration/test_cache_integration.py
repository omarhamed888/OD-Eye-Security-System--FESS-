import pytest
from src.cache.redis_cache import RedisCache
from src.cache.face_cache import FaceCache
import numpy as np
from unittest.mock import patch, MagicMock

class TestCacheIntegration:
    """Tests verify that our cache layers interact correctly."""
    
    @patch('redis.Redis')
    def test_face_cache_flow(self, mock_redis_class):
        """Test the full flow from FaceCache to RedisCache."""
        # Setup mocks
        mock_instance = mock_redis_class.return_value
        mock_instance.ping.return_value = True
        
        # Initialize
        redis_wrapper = RedisCache()
        face_cache = FaceCache(redis_client=redis_wrapper)
        
        # Data to cache
        face_id = "test_user_001"
        encoding = np.random.rand(128)
        metadata = {"name": "Omer", "role": "admin"}
        
        # 1. Test Caching
        with patch.object(redis_wrapper, 'set', return_value=True) as mock_set:
            result = face_cache.cache_face(face_id, encoding, metadata)
            assert result is True
            mock_set.assert_called_once()
            
        # 2. Test Retrieval
        with patch.object(redis_wrapper, 'get') as mock_get:
            mock_get.return_value = {
                "encoding": encoding.tolist(),
                "metadata": metadata
            }
            cached_data = face_cache.get_face(face_id)
            assert cached_data is not None
            assert cached_data['metadata']['name'] == "Omer"
            assert np.allclose(cached_data['encoding'], encoding)
            
    @patch('redis.Redis')
    def test_cache_miss_handling(self, mock_redis_class):
        """Test how system handles missing cache entries."""
        redis_wrapper = RedisCache()
        face_cache = FaceCache(redis_client=redis_wrapper)
        
        with patch.object(redis_wrapper, 'get', return_value=None):
            result = face_cache.get_face("non_existent")
            assert result is None
