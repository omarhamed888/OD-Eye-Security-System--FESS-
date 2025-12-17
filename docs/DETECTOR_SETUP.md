# Detector Module Setup Guide

This comprehensive guide covers the installation, configuration, and usage of the new RTMDet-based motion detection module with distributed Redis caching.

## 1. Installation

### Pre-requisites
- Python 3.8+
- CUDA-capable GPU (recommended)
- Redis Server (local or remote)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install MMDetection & MMCV
It's recommended to install MMCV using `mim` for better compatibility:
```bash
pip install -U openmim
mim install mmengine
mim install "mmcv>=2.0.0"
pip install "mmdet>=3.0.0"
```

## 2. Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Detector Configuration
DETECTOR_MODEL=rtmdet-tiny
DETECTOR_DEVICE=cuda:0
DETECTOR_SCORE_THRESHOLD=0.5
DETECTOR_NMS_THRESHOLD=0.45

# Cache Configuration
CACHE_FACE_TTL=3600
CACHE_DETECTION_TTL=300
CACHE_MAX_FACES=10000

# App Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Model Config & Checkpoints
You need to download the config and checkpoint files for RTMDet.
Default paths:
- Config: `configs/rtmdet_tiny_8xb32-300e_coco.py`
- Checkpoint: `checkpoints/rtmdet_tiny_8xb32-300e_coco.pth`

Download them from the [MMDetection Model Zoo](https://github.com/open-mmlab/mmdetection/tree/main/configs/rtmdet).

## 3. Usage Examples

### Basic Detection
```python
import cv2
from src.models.rtmdet_detector import RTMDetDetector

# Initialize
detector = RTMDetDetector()

# Load image
img = cv2.imread('test.jpg')

# Detect
detections = detector.detect(img)

for det in detections:
    print(f"Found {det.class_name} ({det.confidence:.2f}) at {det.bbox}")
```

### Using Face Cache
```python
from src.cache.face_cache import FaceCache
import numpy as np

cache = FaceCache()

# Cache a face
face_id = "user_123"
encoding = np.random.rand(128)
metadata = {"name": "John Doe", "role": "admin"}

cache.cache_face(face_id, encoding, metadata)

# Retrieve
data = cache.get_face(face_id)
if data:
    print(f"Found: {data['metadata']['name']}")
```

## 4. Running Tests
Run the comprehensive test suite:

```bash
pytest tests/
```

## 5. Troubleshooting

**Issue: Redis Connection Error**
- Ensure Redis server is running: `redis-cli ping`
- Check `REDIS_HOST` and `REDIS_PORT` in `.env`.

**Issue: CUDA OOM (Out of Memory)**
- Switch `DETECTOR_DEVICE` to `cpu` in `.env`.
- Use a smaller model (e.g., RTMDet-tiny).

**Issue: MMDetection Registry Errors**
- Verify `mmcv` and `mmdet` versions match.
- Reinstall using `mim` (see Installation section).
