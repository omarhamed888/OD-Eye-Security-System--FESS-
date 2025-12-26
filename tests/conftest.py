import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis = Mock()
    redis.client = Mock()
    redis.client.ping.return_value = True
    redis.get.return_value = None
    redis.set.return_value = True
    redis.exists.return_value = False
    redis.delete.return_value = True
    return redis

@pytest.fixture
def mock_kafka():
    """Mock Kafka producer."""
    kafka = Mock()
    kafka.producer = Mock()
    kafka.producer.bootstrap_connected.return_value = True
    kafka.send_event.return_value = True
    return kafka

@pytest.fixture
def sample_frame():
    """Sample video frame for testing (640x640 RGB)."""
    return np.zeros((640, 640, 3), dtype=np.uint8)

@pytest.fixture
def sample_detection():
    """Sample detection result."""
    from src.models.base_detector import Detection
    return Detection(
        bbox=(100, 100, 200, 200),
        confidence=0.95,
        class_id=0,
        class_name="person"
    )

@pytest.fixture
def sample_face_encoding():
    """Sample face encoding (128-d vector)."""
    return np.random.rand(128)
