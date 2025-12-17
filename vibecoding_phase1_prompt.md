# FESS Phase 1: Technical Specification & Prompt Reference

**Detailed Technical Requirements for All 9 Tasks**

---

## OVERVIEW

This document provides complete technical specifications for all Phase 1 implementation tasks. Use this as a reference when implementing or customizing the vibecoding prompts.

---

## TASK BREAKDOWN

Phase 1 consists of **9 major tasks** organized into **4 prompts**:

### PROMPT 1 (Tasks 1-3): Detection & Caching Foundation
1. RTMDet Object Detector
2. Redis Distributed Cache
3. Configuration Management

### PROMPT 2 (Tasks 4-7): Events & Monitoring
4. Event Schemas & Data Models
5. Kafka Event Producer
6. Prometheus Metrics
7. Health Monitoring System

### PROMPT 3 (Task 8): Containerization
8. Docker & Docker Compose

### PROMPT 4 (Task 9): Testing Infrastructure
9. Comprehensive Test Suite

---

## TASK 1: RTMDet Object Detector

### Requirements

**Functional:**
- Detect objects in video frames using RTMDet
- Support multiple object classes (person, car, bicycle, etc.)
- Confidence threshold filtering
- GPU and CPU device support
- Model warmup on initialization

**Performance:**
- <100ms detection latency per frame
- 4x faster than YOLOv8n (baseline)
- Support 640x640 and 1280x1280 input sizes
- Batch processing capability (optional)

**Technical:**
- Use MMDetection 3.0+ framework
- RTMDet-tiny for speed, RTMDet-m for accuracy
- Type hints on all functions
- Comprehensive error handling
- Structured logging

### Deliverables
- `src/models/base_detector.py` - Abstract base class
- `src/models/rtmdet_detector.py` - RTMDet implementation  
- `tests/test_rtmdet_detector.py` - Unit tests (>90% coverage)
- `docs/DETECTOR_SETUP.md` - Installation & usage guide

### Code Quality Standards
- 100% type hints
- Google-style docstrings
- PEP 8 compliant
- No print statements (use logging)
- Graceful degradation on errors

---

## TASK 2: Redis Distributed Cache

### Requirements

**Functional:**
- Connection pooling (max 50 connections)
- get/set/delete/exists operations
- TTL support for expiring keys
- Pickle and JSON serialization
- Face encoding storage
- Metadata storage alongside encodings

**Performance:**
- <5ms cache lookup
- 90% cache hit rate (target)
- Support 10,000+ cached faces
- Connection timeout: 5 seconds

**Technical:**
- redis-py library
- Connection pool with automatic reconnection
- Error handling for connection failures
- Structured logging for cache operations

### Deliverables
- `src/cache/redis_cache.py` - Redis client wrapper
- `src/cache/face_cache.py` - Face-specific caching logic
- `tests/test_redis_cache.py` - Unit tests with mocks
- `tests/test_face_cache.py` - Integration tests

### Cache Key Schema
```
face:{face_id} → {encoding, metadata, cached_at}
detection:{camera_id}:{frame_number} → {detections, timestamp}
```

---

## TASK 3: Configuration Management

### Requirements

**Functional:**
- Environment variable support
- YAML/JSON config file support
- Default values for all settings
- Validation on load
- Nested configuration structure
- Secrets management (passwords, API keys)

**Configuration Categories:**
- Redis settings (host, port, password, etc.)
- Detector settings (model, device, thresholds)
- Cache settings (TTLs, max sizes)
- Kafka settings (brokers, topics, etc.)
- Application settings (log level, environment)

**Technical:**
- Pydantic 2.0+ for validation
- pydantic-settings for environment variables
- Type-safe access to config
- Singleton pattern for global settings

### Deliverables
- `src/config/settings.py` - Pydantic settings classes
- `src/config/config.yaml.example` - Example configuration
- `.env.example` - Example environment variables
- `tests/test_settings.py` - Configuration tests

### Example Settings Structure
```python
class Settings(BaseSettings):
    redis: RedisSettings
    detector: DetectorSettings
    cache: CacheSettings
    kafka: KafkaSettings
    log_level: str
    environment: str
```

---

## TASK 4: Event Schemas & Data Models

### Requirements

**Functional:**
- Pydantic models for all event types
- JSON serializable
- Timestamp generation
- UUID generation for event IDs
- Type validation
- Nested models (e.g., BoundingBox)

**Event Types:**
1. MotionDetectionEvent
2. FaceRecognitionEvent
3. AlertEvent
4. SystemStatusEvent (optional)

**Technical:**
- Pydantic BaseModel for all events
- datetime fields with UTC timezone
- Enum for event types
- model_dump() for serialization

### Deliverables
- `src/events/event_schemas.py` - All event models
- `tests/test_event_schemas.py` - Validation tests

### Event Schema Example
```python
class MotionDetectionEvent(BaseModel):
    event_id: str
    event_type: EventType
    timestamp: datetime
    camera_id: str
    frame_number: int
    detected_objects: List[dict]
    total_objects: int
    confidence_scores: List[float]
```

---

## TASK 5: Kafka Event Producer

### Requirements

**Functional:**
- Send events to Kafka topics
- Automatic serialization (JSON)
- Partitioning by camera_id (key)
- Acknowledgment modes (0, 1, all)
- Compression (snappy, gzip)
- Batch sending with linger

**Performance:**
- Async sending capability
- Batch size: 16KB default
- Linger time: 10ms default
- Throughput: >10,000 events/sec

**Topics:**
- `motion.detection.events`
- `face.recognition.events`
- `alert.events`

**Technical:**
- kafka-python library
- Error handling and retries
- Connection monitoring
- Graceful shutdown

### Deliverables
- `src/events/kafka_producer.py` - Low-level producer
- `src/events/event_publisher.py` - High-level API
- `src/config/kafka_settings.py` - Kafka configuration
- `tests/test_kafka_producer.py` - Unit tests (mocked)
- `tests/test_event_publisher.py` - Integration tests

---

## TASK 6: Prometheus Metrics

### Requirements

**Metrics to Expose:**
1. `fess_detections_total` - Counter (camera_id, object_class labels)
2. `fess_detection_latency_seconds` - Histogram (camera_id label)
3. `fess_face_recognitions_total` - Counter (camera_id, authorized labels)
4. `fess_face_cache_hits_total` - Counter
5. `fess_face_cache_misses_total` - Counter
6. `fess_kafka_events_sent_total` - Counter (topic, status labels)
7. `fess_active_cameras` - Gauge
8. `fess_fps` - Gauge (camera_id label)
9. `fess_cpu_usage_percent` - Gauge
10. `fess_memory_usage_bytes` - Gauge

**Technical:**
- prometheus_client library
- Custom registry
- Histogram buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
- HTTP endpoint: `/metrics` (expose format)

### Deliverables
- `src/monitoring/metrics.py` - Metrics definitions
- `tests/test_metrics.py` - Metrics tests

---

## TASK 7: Health Monitoring System

### Requirements

**Health Checks:**
1. Redis connectivity (ping test)
2. Kafka connectivity (bootstrap check)
3. System resources (CPU, memory, disk)
4. Component status aggregation

**Health Statuses:**
- `healthy` - All systems operational
- `degraded` - Some non-critical failures
- `unhealthy` - Critical failures

**Technical:**
- psutil for system metrics
- Individual component checkers
- Overall health aggregation
- JSON response format
- HTTP endpoint: `/health`

### Deliverables
- `src/monitoring/health.py` - Health checker
- `tests/test_health.py` - Health check tests

### Health Response Example
```json
{
  "status": "healthy",
  "timestamp": "2024-12-17T18:00:00Z",
  "components": {
    "redis": {"healthy": true, "latency_ms": 2},
    "kafka": {"healthy": true},
    "system": {"healthy": true, "cpu_percent": 15.2, "memory_percent": 42.1}
  }
}
```

---

## TASK 8: Docker & Docker Compose

### Requirements

**Dockerfile:**
- Multi-stage build (optional)
- Python 3.10+ base image
- RTMDet model download in build
- Optimized layers (<2GB final image)
- Non-root user
- Health check instruction

**docker-compose.yml Services:**
1. `detector` - Your application
2. `redis` - Cache backend
3. `kafka` - Event streaming
4. `prometheus` - Metrics collection (optional)

**Networking:**
- Services on same network
- Port mappings for external access
- Environment variable injection

**Volumes:**
- Model persistence
- Log persistence
- Known faces persistence

### Deliverables
- `Dockerfile` - Optimized multi-stage build
- `.dockerignore` - Exclude unnecessary files
- `docker-compose.yml` - Multi-service orchestration
- `docker/entrypoint.sh` - Container startup script
- `docs/DOCKER_SETUP.md` - Usage instructions

###Dockerfile Best Practices
- Use slim base images
- Copy requirements first (layer caching)
- Multi-stage for build dependencies
- Health check with curl/wget
- Metadata labels

---

## TASK 9: Comprehensive Test Suite

### Requirements

**Test Types:**
1. Unit Tests (>90% coverage)
   - All modules tested independently
   - Mock external dependencies
   - Fast execution (<10 seconds total)

2. Integration Tests
   - Redis integration
   - Kafka integration
   - End-to-end detection flow

3. Performance Tests (optional)
   - Detection latency benchmarks
   - FPS measurements
   - Cache performance tests

**Test Organization:**
```
tests/
├── unit/
│   ├── test_detector.py
│   ├── test_cache.py
│   ├── test_events.py
│   └── test_metrics.py
├── integration/
│   ├── test_detector_cache.py
│   ├── test_events_kafka.py
│   └── test_end_to_end.py
├── performance/ (optional)
│   └── test_benchmarks.py
└── conftest.py (pytest fixtures)
```

**Tools:**
- pytest for test framework
- pytest-cov for coverage
- pytest-mock for mocking
- unittest.mock for complex mocks

### Deliverables
- Complete test suite (>85% overall coverage)
- `pytest.ini` - Pytest configuration
- `conftest.py` - Shared fixtures
- `requirements-dev.txt` - Dev dependencies

### Coverage Targets
- `src/models/` - >90%
- `src/cache/` - >90%
- `src/events/` - >85%
- `src/monitoring/` - >85%
- `src/config/` - >80%
- **Overall:** >85%

---

## QUALITY STANDARDS (All Tasks)

### Code Quality
✅ 100% type hints on all functions/methods  
✅ Google-style docstrings  
✅ PEP 8 compliant code  
✅ No print() statements (use logging)  
✅ Specific exception handling  
✅ Comprehensive error messages  

### Testing
✅ >85% overall coverage  
✅ Unit tests for all modules  
✅ Integration tests for external services  
✅ Mock external dependencies  
✅ Fast test execution  

### Documentation
✅ README for each major component  
✅ Configuration examples  
✅ Usage examples  
✅ Installation instructions  

### Performance
✅ Detection latency <100ms  
✅ Cache lookup <5ms  
✅ Event publishing <10ms  
✅ Memory usage <2GB total  
✅ CPU usage <10% per camera  

---

## INTEGRATION POINTS

### Between Tasks

1. **Detector → Cache:**
   - Detector uses FaceCache to store/retrieve encodings
   - Cache key: `face:{face_id}`

2. **Detector → Events:**
   - Detector publishes MotionDetectionEvent via EventPublisher
   - Detector publishes FaceRecognitionEvent for each face

3. **Events → Metrics:**
   - EventPublisher increments `kafka_events_sent_total`
   - Detector increments `detections_total`, records `detection_latency`

4. **All → Config:**
   - All modules read from `settings` singleton
   - Environment variable overrides

5. **All → Health:**
   - HealthChecker monitors Redis, Kafka, System
   - Aggregates overall health status

---

## TECHNOLOGY REQUIREMENTS

### Python Packages
```
mmdet>=3.0.0
mmcv>=2.0.0
torch>=2.0.0
redis>=4.5.0
kafka-python>=2.0.2
pydantic>=2.0.0
pydantic-settings>=2.0.0
prometheus-client>=0.17.0
psutil>=5.9.0
pytest>=7.3.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
numpy>=1.24.0
opencv-python>=4.7.0
```

### System Requirements
- Python 3.10+
- Docker 20.10+
- docker-compose 2.0+
- 8GB RAM minimum
- GPU (optional, for faster detection)

---

## SUCCESS CRITERIA

### Functional
✅ Run 10+ camera streams  
✅ Detect motion <100ms  
✅ Alert <500ms end-to-end  
✅ Cache faces in Redis  
✅ Publish events to Kafka  
✅ Expose Prometheus metrics  
✅ Health check endpoint functional  
✅ Run via `docker-compose up`  

### Performance
✅ 300+ FPS total throughput  
✅ <10% CPU per camera  
✅ <2GB Docker image  
✅ >90% cache hit rate  

### Quality
✅ >85% test coverage  
✅ 100% type hints  
✅ No linter errors  
✅ Comprehensive documentation  

---

*This is the technical reference for FESS Phase 1 Vibecoding Implementation*  
*Use this document to understand requirements and customize prompts as needed*
