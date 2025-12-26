# Event Streaming & Monitoring Setup

This guide covers the Kafka event streaming and Prometheus monitoring infrastructure for FESS.

## 1. Architecture Overview

FESS uses:
- **Kafka**: For real-time event streaming (motion, face recognition, alerts)
- **Prometheus**: For metrics collection and monitoring
- **Health Checks**: For system component status monitoring

## 2. Kafka Setup

### Local Development (Docker)

Start Kafka using Docker:
```bash
docker run -d --name kafka \
  -p 9092:9092 \
  apache/kafka:latest
```

### Configuration

Set environment variables in `.env`:
```env
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_MOTION=motion.detection.events
KAFKA_TOPIC_FACES=face.recognition.events
KAFKA_TOPIC_ALERTS=alert.events

# Producer Settings
KAFKA_ACKS=1
KAFKA_COMPRESSION=snappy
KAFKA_LINGER_MS=10
KAFKA_BATCH_SIZE=16384
```

## 3. Event Schemas

### Motion Detection Event
```python
{
  "event_id": "uuid",
  "event_type": "motion.detected",
  "timestamp": "2024-01-01T12:00:00",
  "camera_id": "cam_01",
  "frame_number": 1234,
  "detected_objects": [...],
  "total_objects": 3,
  "confidence_scores": [0.95, 0.87, 0.92]
}
```

### Face Recognition Event
```python
{
  "event_id": "uuid",
  "event_type": "face.recognized",
  "timestamp": "2024-01-01T12:00:00",
  "camera_id": "cam_01",
  "frame_number": 1235,
  "face_id": "face_123",
  "person_name": "John Doe",
  "confidence": 0.98,
  "bbox": {"x1": 10, "y1": 20, "x2": 30, "y2": 40},
  "is_authorized": true
}
```

### Alert Event
```python
{
  "event_id": "uuid",
  "event_type": "alert.triggered",
  "timestamp": "2024-01-01T12:00:00",
  "camera_id": "cam_01",
  "alert_level": "CRITICAL",
  "alert_message": "Unauthorized access detected",
  "associated_events": ["event_1", "event_2"]
}
```

## 4. Usage Examples

### Publishing Events

```python
from src.events.event_publisher import EventPublisher

# Initialize publisher
publisher = EventPublisher()

# Publish motion event
publisher.publish_motion_event(
    camera_id="cam_01",
    frame_number=1234,
    detected_objects=[{"class": "person", "bbox": [0, 0, 100, 100]}],
    confidence_scores=[0.95]
)

# Publish face event
publisher.publish_face_event(
    camera_id="cam_01",
    frame_number=1235,
    face_id="face_123",
    bbox=(10, 20, 30, 40),
    confidence=0.98,
    person_name="John Doe",
    is_authorized=True
)

# Publish alert
publisher.publish_alert(
    camera_id="cam_01",
    alert_level="CRITICAL",
    message="Unauthorized access detected"
)

# Close when done
publisher.close()
```

## 5. Prometheus Metrics

### Available Metrics

- `fess_detections_total`: Total detections (by camera, object class)
- `fess_detection_latency_seconds`: Detection processing time
- `fess_face_recognitions_total`: Face recognitions (by camera, authorization status)
- `fess_face_cache_hits_total`: Cache hit count
- `fess_face_cache_misses_total`: Cache miss count
- `fess_kafka_events_sent_total`: Kafka events sent (by topic, status)
- `fess_active_cameras`: Number of active cameras
- `fess_fps`: FPS per camera
- `fess_memory_usage_bytes`: System memory usage
- `fess_cpu_usage_percent`: CPU usage percentage

### Accessing Metrics

```python
from src.monitoring.metrics import get_metrics, get_content_type

# Get metrics in Prometheus format
metrics = get_metrics()
content_type = get_content_type()

# Example: Expose via HTTP endpoint
# (You would integrate this with Flask/FastAPI)
```

### Using Metrics

```python
from src.monitoring import metrics

# Increment detection counter
metrics.detections_total.labels(
    camera_id="cam_01",
    object_class="person"
).inc()

# Record detection latency
with metrics.detection_latency.labels(camera_id="cam_01").time():
    # Your detection code here
    pass

# Update system metrics
metrics.cpu_usage_percent.set(45.2)
metrics.memory_usage_bytes.set(1024 * 1024 * 512)  # 512 MB
```

## 6. Health Checks

### Using the Health Checker

```python
from src.monitoring.health import HealthChecker
from src.cache.redis_cache import RedisCache
from src.events.kafka_producer import KafkaEventProducer

# Initialize components
redis = RedisCache()
kafka = KafkaEventProducer()

# Create health checker
health_checker = HealthChecker(
    redis_client=redis,
    kafka_producer=kafka
)

# Get overall health status
status = health_checker.get_health_status()
print(status)
```

### Health Status Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "components": {
    "redis": {
      "status": "healthy",
      "healthy": true,
      "latency_ms": 0
    },
    "kafka": {
      "status": "healthy",
      "healthy": true
    },
    "system": {
      "status": "healthy",
      "healthy": true,
      "cpu_percent": 25.3,
      "memory_percent": 45.2,
      "memory_available_mb": 8192,
      "disk_percent": 60.5,
      "disk_free_gb": 50.2
    }
  }
}
```

## 7. Testing

Run all tests:
```bash
pytest tests/ -v --cov=src
```

Run specific test modules:
```bash
pytest tests/test_kafka_producer.py -v
pytest tests/test_event_publisher.py -v
pytest tests/test_health_checker.py -v
```

## 8. Troubleshooting

### Kafka Connection Issues

**Problem**: Cannot connect to Kafka broker

**Solution**:
- Ensure Kafka is running: `docker ps | grep kafka`
- Check `KAFKA_BOOTSTRAP_SERVERS` in `.env`
- Verify network connectivity: `telnet localhost 9092`

### Event Serialization Errors

**Problem**: `TypeError` when sending events

**Solution**:
- Ensure all datetime objects are properly handled
- Use `model_dump()` for Pydantic models
- Check JSON serialization compatibility

### Metrics Not Updating

**Problem**: Prometheus metrics show 0 or don't update

**Solution**:
- Verify metrics are being called in your code
- Check metric labels match exactly
- Ensure registry is properly initialized

## 9. Production Considerations

### Kafka
- Use a managed Kafka service (AWS MSK, Confluent Cloud) for production
- Configure appropriate replication factors
- Enable authentication and encryption
- Set up monitoring and alerting

### Prometheus
- Deploy Prometheus server for metrics collection
- Configure scrape intervals appropriately
- Set up Grafana dashboards for visualization
- Configure alerting rules

### Health Checks
- Expose health endpoint via HTTP
- Integrate with load balancers (for liveness/readiness probes)
- Set up automated health monitoring
- Configure alerts for degraded states

## 10. Integration Example

```python
from src.models.rtmdet_detector import RTMDetDetector
from src.events.event_publisher import EventPublisher
from src.monitoring import metrics
from src.monitoring.health import HealthChecker

# Initialize components
detector = RTMDetDetector()
publisher = EventPublisher()
health_checker = HealthChecker()

# Main processing loop
def process_frame(frame, camera_id, frame_number):
    # Time detection
    with metrics.detection_latency.labels(camera_id=camera_id).time():
        detections = detector.detect(frame)
    
    # Update metrics
    for det in detections:
        metrics.detections_total.labels(
            camera_id=camera_id,
            object_class=det.class_name
        ).inc()
    
    # Publish event
    if detections:
        publisher.publish_motion_event(
            camera_id=camera_id,
            frame_number=frame_number,
            detected_objects=[d.to_dict() for d in detections],
            confidence_scores=[d.confidence for d in detections]
        )
        
        # Update Kafka metrics
        metrics.kafka_events_sent.labels(
            topic="motion.detection.events",
            status="success"
        ).inc()
```

## 11. Next Steps

After completing Event Streaming & Monitoring setup:
1. ✅ Verify Kafka is running and accessible
2. ✅ Test event publishing with sample data
3. ✅ Check Prometheus metrics endpoint
4. ✅ Verify health checks return correct status
5. ✅ Run all tests and ensure they pass
6. → Proceed to **PROMPT 3**: Docker Containerization
