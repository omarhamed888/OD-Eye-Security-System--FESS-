import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from src.events.kafka_producer import KafkaEventProducer
from src.events.event_publisher import EventPublisher
from src.monitoring.health import HealthChecker
from src.cache.redis_cache import RedisCache
from src.cache.face_cache import FaceCache
import redis
import json

def test_kafka_producer_error_handling():
    """Test kafka producer error scenarios."""
    with patch('src.events.kafka_producer.KafkaProducer') as mock_producer:
        mock_instance = mock_producer.return_value
        mock_instance.send.side_effect = Exception("Kafka Error")
        
        producer = KafkaEventProducer()
        res = producer.send_event("test_topic", {"data": "test"})
        assert res is False

def test_health_checker_system_failure():
    """Test health checker when psutil fails."""
    with patch('psutil.cpu_percent', side_effect=Exception("OS Error")):
        checker = HealthChecker(MagicMock(), MagicMock())
        status = checker.check_system_resources()
        assert status['healthy'] is False

def test_publisher_all_events():
    """Test all publisher methods."""
    mock_producer = MagicMock()
    mock_producer.send_event.return_value = True
    pub = EventPublisher(kafka_producer=mock_producer)
    
    # Motion
    assert pub.publish_motion_event("cam1", 1, [], []) is True
    
    # Face
    assert pub.publish_face_event("cam1", 1, "face1", (10, 10, 50, 50), 0.9, person_name="Person A", is_authorized=True) is True
    
    # Alert
    assert pub.publish_alert("cam1", "CRITICAL", "Intruder", []) is True

def test_redis_cache_extended():
    """Test RedisCache edge cases and JSON serialization."""
    with patch('redis.Redis') as mock_redis_cls, \
         patch('redis.connection.ConnectionPool') as mock_pool:
        
        mock_client = mock_redis_cls.return_value
        # 1. Connection Error
        mock_client.ping.side_effect = redis.ConnectionError("Conn Error")
        with pytest.raises(redis.ConnectionError):
            RedisCache()
        
        # 2. Setup healthy client
        mock_client.ping.side_effect = None
        cache = RedisCache()
        
        # 3. JSON Serialization
        cache.set("json_key", {"a": 1}, serialize="json")
        mock_client.set.assert_called()
        
        # 4. JSON Deserialization
        mock_client.get.return_value = json.dumps({"a": 1}).encode('utf-8')
        val = cache.get("json_key", deserialize="json")
        assert val == {"a": 1}
        
        # 5. Unknown serialization
        assert cache.set("key", "val", serialize="unknown") is False
        assert cache.get("key", deserialize="unknown") is None
        
        # 6. Error handling for delete/exists
        mock_client.delete.side_effect = Exception("Delete fail")
        assert cache.delete("key") is False
        
        mock_client.exists.side_effect = Exception("Exists fail")
        assert cache.exists("key") is False

def test_face_cache_extended():
    """Test FaceCache error scenarios."""
    mock_redis = MagicMock()
    fc = FaceCache(redis_client=mock_redis)
    
    # 1. cache_face failure (return False from redis)
    mock_redis.set.return_value = False
    assert fc.cache_face("f1", np.array([0.1, 0.2])) is False
    
    # 2. cache_face exception
    mock_redis.set.side_effect = Exception("Crash")
    assert fc.cache_face("f1", np.array([0.1, 0.2])) is False
    
    # 3. get_face exception
    mock_redis.get.side_effect = Exception("Crash")
    assert fc.get_face("f1") is None
    
    # 4. delete and exists
    fc.delete_face("f1")
    mock_redis.delete.assert_called_with("face:f1")
    
    fc.face_exists("f1")
    mock_redis.exists.assert_called_with("face:f1")

def test_health_checker_extended():
    """Test health checker with missing components."""
    # 1. No redis/kafka configured
    checker = HealthChecker(redis_client=None, kafka_producer=None)
    status = checker.get_health_status()
    assert status['components']['redis']['status'] == "not_configured"
    assert status['components']['kafka']['status'] == "not_configured"
    
    # 2. Kafka unhealthy (bootstrap_connected returns False)
    mock_kafka = MagicMock()
    mock_kafka.producer.bootstrap_connected.return_value = False
    checker = HealthChecker(kafka_producer=mock_kafka)
    res = checker.check_kafka()
    assert res['status'] == "unhealthy"
    assert res['healthy'] is False

def test_kafka_producer_extended():
    """Test KafkaProducer flush, close and unexpected errors."""
    with patch('src.events.kafka_producer.KafkaProducer') as mock_producer_cls:
        mock_instance = mock_producer_cls.return_value
        producer = KafkaEventProducer()
        
        # 1. Flush success/error
        producer.flush()
        mock_instance.flush.assert_called()
        
        mock_instance.flush.side_effect = Exception("Flush error")
        producer.flush() # Should not raise
        
        # 2. Close success/error
        producer.close()
        mock_instance.close.assert_called()
        
        mock_instance.close.side_effect = Exception("Close error")
        producer.close() # Should not raise
        
        # 3. Unexpected error in send_event
        mock_instance.send.side_effect = Exception("Unexpected")
        assert producer.send_event("t", {}) is False

def test_event_publisher_exceptions():
    """Test EventPublisher exception paths."""
    mock_kafka = MagicMock()
    pub = EventPublisher(kafka_producer=mock_kafka)
    
    # 1. publish_motion_event exception (e.g. invalid objects list)
    with patch('src.events.event_publisher.MotionDetectionEvent', side_effect=Exception("Schema error")):
        assert pub.publish_motion_event("c1", 1, [], []) is False
    
    # 2. publish_alert exception
    with patch('src.events.event_publisher.AlertEvent', side_effect=Exception("Schema error")):
        assert pub.publish_alert("c1", "LVL", "msg") is False
