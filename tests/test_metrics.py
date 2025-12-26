import pytest
from src.monitoring import metrics

def test_metrics_registry():
    """Verify metrics are initialized and can be accessed."""
    # Test increments
    metrics.detections_total.labels(camera_id="test", object_class="person").inc()
    metrics.face_recognitions_total.labels(camera_id="test", authorized="true").inc()
    
    # Verify content type and generation
    assert 'text/plain' in metrics.get_content_type()
    assert 'charset=utf-8' in metrics.get_content_type()
    data = metrics.get_metrics()
    assert b'fess_detections_total' in data
    assert b'camera_id="test"' in data
