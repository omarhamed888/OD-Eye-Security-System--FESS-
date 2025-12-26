from src.config.settings import KafkaSettings, RedisSettings

def test_settings_validation():
    """Verify settings validation logic."""
    k = KafkaSettings(bootstrap_servers=["localhost:9092"])
    assert k.bootstrap_servers == ["localhost:9092"]
    
    r = RedisSettings(host="localhost", port=6379)
    assert r.port == 6379

def test_publisher_edge_cases():
    """Test publisher handles no detections."""
    from src.events.event_publisher import EventPublisher
    from unittest.mock import MagicMock
    
    mp = MagicMock()
    mp.send_event.return_value = True
    pub = EventPublisher(kafka_producer=mp)
    
    # Empty detections should still work
    res = pub.publish_motion_event("cam1", 1, [], [])
    assert res is True
