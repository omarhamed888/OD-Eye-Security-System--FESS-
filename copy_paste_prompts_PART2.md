# 🎯 COPY-PASTE PROMPTS FOR FESS PHASE 1 - PART 2

**2 Ready-to-Use Prompts | 30-40 Minutes Total Implementation | Production-Grade Code**

This file contains the remaining prompts (3 & 4) to complete Phase 1 implementation.

---

## 📋 TABLE OF CONTENTS

1. **PROMPT 3:** Docker Containerization + Compose (15-20 min)
2. **PROMPT 4:** Comprehensive Test Suite (15-20 min)

---

## ✅ Prerequisites

Before starting these prompts, ensure you've completed:
- ✅ PROMPT 1: RTMDet Detector + Redis Cache + Config (from copy_paste_prompts.md)
- ✅ PROMPT 2: Kafka Event Producer + Metrics + Health (from copy_paste_prompts.md)

---

# 🐳 PROMPT 3: Docker Containerization + Compose

**Time:** 15-20 minutes  
**Generates:** Production-ready Docker setup  
**Files Created:** 5-6 files

---

## COPY EVERYTHING BELOW THIS LINE ⬇️

```
# PROMPT 3: Docker Containerization + Multi-Service Orchestration

Create production-ready Docker setup with multi-stage builds and docker-compose orchestration for FESS + Redis + Kafka.

## 1. Dockerfile (Multi-Stage Build)

Create an optimized Dockerfile with multi-stage build:

```dockerfile
# Build stage
FROM python:3.10-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Download RTMDet model (optional - for self-contained image)
# RUN mkdir -p /build/checkpoints && \
#     wget -O /build/checkpoints/rtmdet_tiny.pth \
#     https://download.openmmlab.com/mmdetection/v3.0/rtmdet/rtmdet_tiny_8xb32-300e_coco/rtmdet_tiny_8xb32-300e_coco_20220902_112414-78e30dcc.pth

# Runtime stage
FROM python:3.10-slim

LABEL maintainer="your-email@example.com"
LABEL description="FESS Motion Detection System"
LABEL version="1.0.0"

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/
COPY known_faces/ ./known_faces/
COPY configs/ ./configs/
COPY checkpoints/ ./checkpoints/

# Create non-root user
RUN useradd -m -u 1000 fess && \
    chown -R fess:fess /app

USER fess

# Add local Python packages to PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000

# Entry point
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["python", "-m", "src.main"]
```

## 2. Docker Compose (docker-compose.yml)

Create comprehensive multi-service orchestration:

```yaml
version: '3.8'

services:
  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: fess-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - fess-network

  # Kafka (Single-node for development)
  kafka:
    image: apache/kafka:latest
    container_name: fess-kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_NUM_PARTITIONS: 3
    volumes:
      - kafka-data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD-SHELL", "kafka-broker-api-versions.sh --bootstrap-server localhost:9092"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - fess-network

  # FESS Application
  fess:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fess-detector
    ports:
      - "8000:8000"
    environment:
      # Redis
      REDIS_HOST: redis
      REDIS_PORT: 6379
      
      # Kafka
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      KAFKA_TOPIC_MOTION: motion.detection.events
      KAFKA_TOPIC_FACES: face.recognition.events
      KAFKA_TOPIC_ALERTS: alert.events
      
      # Detector
      DETECTOR_DEVICE: cpu
      DETECTOR_SCORE_THRESHOLD: 0.5
      
      # Application
      LOG_LEVEL: INFO
      ENVIRONMENT: production
    volumes:
      - ./src:/app/src  # Hot reload in dev
      - ./known_faces:/app/known_faces
      - ./logs:/app/logs
      - model-cache:/app/checkpoints
    depends_on:
      redis:
        condition: service_healthy
      kafka:
        condition: service_healthy
    networks:
      - fess-network
    restart: unless-stopped

  # Prometheus (Optional - for metrics collection)
  prometheus:
    image: prom/prometheus:latest
    container_name: fess-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - fess-network
    restart: unless-stopped

  # Grafana (Optional - for visualization)
  grafana:
    image: grafana/grafana:latest
    container_name: fess-grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_USERS_ALLOW_SIGN_UP: false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./docker/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./docker/grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus
    networks:
      - fess-network
    restart: unless-stopped

networks:
  fess-network:
    driver: bridge

volumes:
  redis-data:
  kafka-data:
  prometheus-data:
  grafana-data:
  model-cache:
```

## 3. Docker Ignore (.dockerignore)

Optimize build context:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/
ENV/

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover
.hypothesis/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Git
.git/
.gitignore
.gitattributes

# Docker
.dockerignore
Dockerfile
docker-compose*.yml

# Documentation
docs/
*.md
README.md

# Logs
logs/
*.log

# Models (download at runtime instead)
# checkpoints/*.pth

# Development
.env
.env.local
tests/
```

## 4. Entrypoint Script (docker/entrypoint.sh)

Create flexible container startup:

```bash
#!/bin/bash
set -e

echo "🚀 Starting FESS Container..."

# Wait for dependencies
echo "⏳ Waiting for Redis..."
until redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1; do
  echo "   Redis is unavailable - sleeping"
  sleep 2
done
echo "✅ Redis is ready"

echo "⏳ Waiting for Kafka..."
until kafka-broker-api-versions.sh --bootstrap-server ${KAFKA_BOOTSTRAP_SERVERS:-kafka:9092} > /dev/null 2>&1; do
  echo "   Kafka is unavailable - sleeping"
  sleep 5
done
echo "✅ Kafka is ready"

# Download models if not present (optional)
if [ ! -f "/app/checkpoints/rtmdet_tiny.pth" ]; then
  echo "📥 Downloading RTMDet model..."
  mkdir -p /app/checkpoints
  # wget -O /app/checkpoints/rtmdet_tiny.pth <MODEL_URL>
  echo "⚠️  Model download skipped (add URL in entrypoint.sh)"
fi

# Create necessary directories
mkdir -p /app/logs
mkdir -p /app/known_faces

# Set permissions
chown -R fess:fess /app/logs /app/known_faces

echo "✅ All dependencies ready"
echo "🎬 Starting FESS application..."

# Execute the main command
exec "$@"
```

## 5. Prometheus Configuration (docker/prometheus.yml)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'fess'
    static_configs:
      - targets: ['fess:8000']
    metrics_path: '/metrics'
```

## 6. Environment Variables (.env.production)

Template for production environment:

```env
# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MAX_CONNECTIONS=50

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_MOTION=motion.detection.events
KAFKA_TOPIC_FACES=face.recognition.events
KAFKA_TOPIC_ALERTS=alert.events
KAFKA_ACKS=1
KAFKA_COMPRESSION=snappy

# Detector Configuration
DETECTOR_MODEL=rtmdet-tiny
DETECTOR_DEVICE=cpu
DETECTOR_SCORE_THRESHOLD=0.5
DETECTOR_NMS_THRESHOLD=0.45

# Cache Configuration
CACHE_FACE_TTL=3600
CACHE_DETECTION_TTL=300
CACHE_MAX_FACES=10000

# Application
LOG_LEVEL=INFO
ENVIRONMENT=production
```

## 7. Documentation (docs/DOCKER_SETUP.md)

Create comprehensive Docker documentation:

```markdown
# Docker Setup Guide

## Quick Start

1. **Build and start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Check service health:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f fess
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

## Development Mode

Run with hot-reload:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Production Deployment

1. **Build optimized image:**
   ```bash
   docker build -t fess:latest .
   ```

2. **Use production compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Scale detectors:**
   ```bash
   docker-compose up -d --scale fess=3
   ```

## Accessing Services

- **FESS API:** http://localhost:8000
- **Health Check:** http://localhost:8000/health
- **Metrics:** http://localhost:8000/metrics
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin)
- **Redis:** localhost:6379
- **Kafka:** localhost:9092

## Troubleshooting

### Container won't start
```bash
docker-compose logs fess
```

### Redis connection issues
```bash
docker-compose exec redis redis-cli ping
```

### Kafka connection issues
```bash
docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Clear all data
```bash
docker-compose down -v
```
```

## DELIVERABLES

Provide:
1. Production-ready Dockerfile (multi-stage)
2. docker-compose.yml with all services
3. .dockerignore for optimized builds
4. Entrypoint script with health checks
5. Prometheus configuration
6. Complete documentation

Ensure:
- Image size < 2GB
- Health checks configured
- Non-root user
- Proper networking
- Volume persistence
- Environment variable configuration
```

---

## ✅ AFTER PROMPT 3

1. **Build the image:**
   ```bash
   docker build -t fess:latest .
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Verify all services:**
   ```bash
   docker-compose ps
   ```

4. **Check health:**
   ```bash
   curl http://localhost:8000/health
   ```

5. **View metrics:**
   ```bash
   curl http://localhost:8000/metrics
   ```

6. **Commit to git**

7. **Proceed to PROMPT 4**

---

---

# 🧪 PROMPT 4: Comprehensive Test Suite

**Time:** 15-20 minutes  
**Generates:** Complete testing infrastructure  
**Files Created:** 8-10 files

---

## COPY EVERYTHING BELOW THIS LINE ⬇️

```
# PROMPT 4: Comprehensive Test Suite + CI/CD

Create comprehensive testing infrastructure with >85% coverage, integration tests, and CI/CD pipeline.

## 1. Test Organization

Create structured test directory:

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_detector.py
│   ├── test_cache.py
│   ├── test_events.py
│   ├── test_metrics.py
│   └── test_health.py
├── integration/
│   ├── __init__.py
│   ├── test_redis_integration.py
│   ├── test_kafka_integration.py
│   └── test_end_to_end.py
└── performance/ (optional)
    ├── __init__.py
    └── test_benchmarks.py
```

## 2. Enhanced Conftest (tests/conftest.py)

Add comprehensive fixtures:

```python
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
    """Sample video frame for testing."""
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
    """Sample face encoding."""
    return np.random.rand(128)

@pytest.fixture(scope="session")
def docker_services():
    """Start Docker services for integration tests."""
    import subprocess
    
    # Start services
    subprocess.run(["docker-compose", "up", "-d", "redis", "kafka"])
    yield
    # Cleanup
    subprocess.run(["docker-compose", "down"])
```

## 3. Integration Tests

### Redis Integration (tests/integration/test_redis_integration.py)

```python
import pytest
from src.cache.redis_cache import RedisCache
from src.cache.face_cache import FaceCache
import numpy as np

@pytest.mark.integration
class TestRedisIntegration:
    """Integration tests requiring real Redis."""
    
    @pytest.fixture(scope="class")
    def redis_client(self, docker_services):
        """Real Redis client for integration tests."""
        client = RedisCache(host="localhost", port=6379)
        yield client
        client.close()
    
    def test_redis_connection(self, redis_client):
        """Test Redis connectivity."""
        assert redis_client.client.ping() is True
    
    def test_set_and_get(self, redis_client):
        """Test set and get operations."""
        key = "test_key"
        value = {"data": "test_value"}
        
        # Set
        assert redis_client.set(key, value) is True
        
        # Get
        result = redis_client.get(key)
        assert result == value
        
        # Cleanup
        redis_client.delete(key)
    
    def test_face_cache_integration(self, redis_client):
        """Test face caching with real Redis."""
        face_cache = FaceCache(redis_client=redis_client)
        
        face_id = "test_face_123"
        encoding = np.random.rand(128)
        metadata = {"name": "Test User"}
        
        # Cache
        assert face_cache.cache_face(face_id, encoding, metadata) is True
        
        # Retrieve
        cached = face_cache.get_face(face_id)
        assert cached is not None
        assert cached['metadata']['name'] == "Test User"
        assert np.array_equal(cached['encoding'], encoding)
        
        # Cleanup
        face_cache.delete_face(face_id)
```

### Kafka Integration (tests/integration/test_kafka_integration.py)

```python
import pytest
from src.events.kafka_producer import KafkaEventProducer
from src.events.event_publisher import EventPublisher
import time

@pytest.mark.integration
class TestKafkaIntegration:
    """Integration tests requiring real Kafka."""
    
    @pytest.fixture(scope="class")
    def kafka_producer(self, docker_services):
        """Real Kafka producer."""
        # Wait for Kafka to be ready
        time.sleep(10)
        producer = KafkaEventProducer(bootstrap_servers=["localhost:9092"])
        yield producer
        producer.close()
    
    def test_kafka_connection(self, kafka_producer):
        """Test Kafka connectivity."""
        assert kafka_producer.producer.bootstrap_connected() is True
    
    def test_send_event(self, kafka_producer):
        """Test sending event to Kafka."""
        topic = "test_topic"
        event = {"test": "data", "timestamp": "2024-01-01T00:00:00"}
        
        result = kafka_producer.send_event(topic, event, key="test_key")
        assert result is True
    
    def test_event_publisher_integration(self, kafka_producer):
        """Test event publisher with real Kafka."""
        publisher = EventPublisher(kafka_producer=kafka_producer)
        
        result = publisher.publish_motion_event(
            camera_id="test_cam",
            frame_number=1,
            detected_objects=[{"class": "person"}],
            confidence_scores=[0.95]
        )
        
        assert result is True
```

### End-to-End Test (tests/integration/test_end_to_end.py)

```python
import pytest
import numpy as np
from src.models.rtmdet_detector import RTMDetDetector
from src.cache.face_cache import FaceCache
from src.events.event_publisher import EventPublisher
from src.monitoring.health import HealthChecker

@pytest.mark.integration
@pytest.mark.e2e
class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_full_detection_pipeline(self, docker_services, mock_redis, mock_kafka):
        """Test complete detection → cache → event flow."""
        # Setup
        # detector = RTMDetDetector()  # Requires model files
        face_cache = FaceCache(redis_client=mock_redis)
        publisher = EventPublisher(kafka_producer=mock_kafka)
        
        # Simulate detection
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        
        # Would normally run:
        # detections = detector.detect(frame)
        
        # Simulate face caching
        face_id = "e2e_test_face"
        encoding = np.random.rand(128)
        assert face_cache.cache_face(face_id, encoding, {"name": "Test"}) is True
        
        # Simulate event publishing
        assert publisher.publish_motion_event(
            camera_id="e2e_cam",
            frame_number=1,
            detected_objects=[],
            confidence_scores=[]
        ) is True
    
    def test_health_check_all_services(self, docker_services, mock_redis, mock_kafka):
        """Test health check with all services."""
        health_checker = HealthChecker(
            redis_client=mock_redis,
            kafka_producer=mock_kafka
        )
        
        status = health_checker.get_health_status()
        
        assert 'status' in status
        assert 'components' in status
        assert 'redis' in status['components']
        assert 'kafka' in status['components']
        assert 'system' in status['components']
```

## 4. Performance Tests (Optional)

### Benchmarks (tests/performance/test_benchmarks.py)

```python
import pytest
import time
import numpy as np
from src.models.rtmdet_detector import RTMDetDetector
from src.cache.redis_cache import RedisCache

@pytest.mark.performance
class TestPerformance:
    """Performance benchmarks."""
    
    @pytest.mark.skip(reason="Requires model files")
    def test_detection_latency(self, benchmark):
        """Benchmark detection latency."""
        detector = RTMDetDetector()
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        
        # Benchmark
        result = benchmark(detector.detect, frame)
        
        # Assert < 100ms
        assert benchmark.stats.mean < 0.1
    
    def test_cache_performance(self, benchmark, mock_redis):
        """Benchmark cache operations."""
        cache = RedisCache()
        cache.client = mock_redis.client
        
        def cache_operation():
            cache.set("bench_key", {"data": "value"})
            cache.get("bench_key")
        
        result = benchmark(cache_operation)
        
        # Assert < 5ms
        assert benchmark.stats.mean < 0.005
```

## 5. Pytest Configuration (pytest.ini)

```ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (require Redis/Kafka)
    e2e: End-to-end tests
    performance: Performance benchmarks
    slow: Slow tests

# Coverage
addopts =
    --verbose
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=85

# Integration test settings
[pytest.integration]
timeout = 60
```

## 6. GitHub Actions CI/CD (.github/workflows/ci.yml)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      kafka:
        image: apache/kafka:latest
        ports:
          - 9092:9092
        env:
          KAFKA_NODE_ID: 1
          KAFKA_PROCESS_ROLES: broker,controller
          KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest-benchmark
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v -m integration
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
  
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install linters
      run: |
        pip install flake8 black mypy
    
    - name: Run flake8
      run: |
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Run black
      run: |
        black --check src/
    
    - name: Run mypy
      run: |
        mypy src/ --ignore-missing-imports
  
  build:
    runs-on: ubuntu-latest
    needs: [test, lint]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t fess:latest .
    
    - name: Test Docker image
      run: |
        docker run --rm fess:latest --version
```

## 7. Coverage Configuration (.coveragerc)

```ini
[run]
source = src
omit =
    */tests/*
    */conftest.py
    */__pycache__/*
    */site-packages/*

[report]
precision = 2
skip_empty = True
sort = Cover

[html]
directory = htmlcov
```

## 8. Requirements - Dev (requirements-dev.txt)

```
# Testing
pytest>=7.3.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-asyncio>=0.21.0
pytest-benchmark>=4.0.0
pytest-timeout>=2.1.0

# Linting & Formatting
flake8>=6.0.0
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0

# Documentation
sphinx>=6.0.0
sphinx-rtd-theme>=1.2.0
```

## DELIVERABLES

Provide:
1. Complete test suite (unit + integration + e2e)
2. >85% code coverage
3. pytest configuration
4. GitHub Actions CI/CD pipeline
5. Performance benchmarks (optional)
6. Documentation for running tests

Ensure:
- All tests pass
- Coverage meets targets
- CI/CD pipeline works
- Integration tests use real services
- Performance benchmarks documented
```

---

## ✅ AFTER PROMPT 4

1. **Run unit tests:**
   ```bash
   pytest tests/unit/ -v
   ```

2. **Run integration tests:**
   ```bash
   docker-compose up -d redis kafka
   pytest tests/integration/ -v -m integration
   ```

3. **Check coverage:**
   ```bash
   pytest tests/ -v --cov=src --cov-report=html
   open htmlcov/index.html
   ```

4. **Run all tests:**
   ```bash
   pytest tests/ -v
   ```

5. **Verify CI/CD:**
   - Push to GitHub
   - Check Actions tab

6. **Commit everything**

7. **🎉 Phase 1 Complete!**

---

## 🎊 PHASE 1 COMPLETION CHECKLIST

After completing all 4 prompts, verify:

### Functional Tests
- [ ] RTMDet detector works with sample images
- [ ] Redis caching stores and retrieves data
- [ ] Kafka events are published successfully
- [ ] Prometheus metrics are exposed
- [ ] Health check endpoint returns valid status
- [ ] Docker containers start successfully
- [ ] All tests pass (>85% coverage)

### Performance Tests
- [ ] Detection latency < 100ms
- [ ] Cache lookup < 5ms
- [ ] Event publishing < 10ms
- [ ] Docker image < 2GB

### Quality Tests
- [ ] All code has type hints
- [ ] No linter errors (flake8, black, mypy)
- [ ] Complete documentation
- [ ] CI/CD pipeline passes

---

**🚀 Congratulations! You've completed FESS Phase 1!**

Next steps:
- Deploy to production environment
- Configure monitoring dashboards
- Set up alerting rules
- Begin Phase 2 (Advanced Features)
