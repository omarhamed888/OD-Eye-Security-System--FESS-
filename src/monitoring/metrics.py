from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST
)
from typing import Optional

# Create custom registry
REGISTRY = CollectorRegistry()

# System info
system_info = Info(
    'fess_system',
    'FESS system information',
    registry=REGISTRY
)

# Detection metrics
detections_total = Counter(
    'fess_detections_total',
    'Total number of detections',
    ['camera_id', 'object_class'],
    registry=REGISTRY
)

detection_latency = Histogram(
    'fess_detection_latency_seconds',
    'Detection processing latency',
    ['camera_id'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=REGISTRY
)

# Face recognition metrics
face_recognitions_total = Counter(
    'fess_face_recognitions_total',
    'Total face recognitions',
    ['camera_id', 'authorized'],
    registry=REGISTRY
)

face_cache_hits = Counter(
    'fess_face_cache_hits_total',
    'Face cache hits',
    registry=REGISTRY
)

face_cache_misses = Counter(
    'fess_face_cache_misses_total',
    'Face cache  misses',
    registry=REGISTRY
)

# Kafka metrics
kafka_events_sent = Counter(
    'fess_kafka_events_sent_total',
    'Total Kafka events sent',
    ['topic', 'status'],
    registry=REGISTRY
)

# System metrics
active_cameras = Gauge(
    'fess_active_cameras',
    'Number of active cameras',
    registry=REGISTRY
)

fps_per_camera = Gauge(
    'fess_fps',
    'Frames per second per camera',
    ['camera_id'],
    registry=REGISTRY
)

memory_usage_bytes = Gauge(
    'fess_memory_usage_bytes',
    'Memory usage in bytes',
    registry=REGISTRY
)

cpu_usage_percent = Gauge(
    'fess_cpu_usage_percent',
    'CPU usage percentage',
    registry=REGISTRY
)

def get_metrics() -> bytes:
    """Get Prometheus metrics in exposition format."""
    return generate_latest(REGISTRY)

def get_content_type() -> str:
    """Get Prometheus content type."""
    return CONTENT_TYPE_LATEST
