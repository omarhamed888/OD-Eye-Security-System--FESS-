🏗️ Complete Architecture & Implementation Plan
Smart Home Security System - Production-Ready Refactor

📋 Table of Contents

System Architecture Overview
Technology Stack
Detailed Component Breakdown
Database Schema
API Design
Frontend Architecture
Real-time Communication
Security & Authentication
Deployment Strategy
Migration Roadmap
Performance Optimization


🎯 System Architecture Overview {#system-architecture}
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  React Frontend (Next.js)                                        │
│  ├── Dashboard (Real-time monitoring)                            │
│  ├── Video Feed (WebRTC/WebSocket)                              │
│  ├── Alerts & Gallery                                            │
│  └── Settings & Controls                                         │
└────────────────────┬────────────────────────────────────────────┘
│ HTTPS/WSS
│
┌────────────────────┴────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Backend                                                 │
│  ├── REST API (Authentication, CRUD, Config)                    │
│  ├── WebSocket Server (Real-time events & video)                │
│  ├── Background Tasks (Detection loop, cleanup)                 │
│  └── API Gateway (Rate limiting, logging)                       │
└────────────────────┬────────────────────────────────────────────┘
│
┌────────────────────┴────────────────────────────────────────────┐
│                       BUSINESS LOGIC LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  Core Services                                                   │
│  ├── Camera Service (OpenCV management)                         │
│  ├── Detection Service (YOLOv8 inference)                       │
│  ├── Face Recognition Service (dlib)                            │
│  ├── Alert Service (Event processing)                           │
│  ├── Notification Service (Telegram, Email, Push)               │
│  └── Storage Service (Image/video management)                   │
└────────────────────┬────────────────────────────────────────────┘
│
┌────────────────────┴────────────────────────────────────────────┐
│                         DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  ├── PostgreSQL (Alerts, Users, Config, Analytics)              │
│  ├── Redis (Caching, Session, Real-time state)                  │
│  └── File System / S3 (Images, Videos, Models)                  │
└─────────────────────────────────────────────────────────────────┘
│
┌────────────────────┴────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                         │
├─────────────────────────────────────────────────────────────────┤
│  ├── Telegram Bot API                                            │
│  ├── Email Service (SMTP)                                        │
│  ├── Push Notification Service (Firebase/OneSignal)             │
│  └── Cloud Storage (AWS S3/MinIO)                               │
└─────────────────────────────────────────────────────────────────┘

🛠️ Technology Stack {#tech-stack}
Backend
yamlCore Framework: FastAPI (Python 3.11+)
- Async/await for high performance
- Automatic API documentation (Swagger/OpenAPI)
- WebSocket support built-in
- Type hints with Pydantic validation

Computer Vision:
- YOLOv8: Object detection (Ultralytics)
- dlib: Face recognition
- OpenCV: Camera handling & image processing

Database & Caching:
- PostgreSQL: Primary database (structured data)
- Redis: Caching, session management, real-time state
- SQLAlchemy: ORM for database operations
- Alembic: Database migrations

Task Queue:
- Celery: Background tasks (long-running operations)
- Redis: Message broker for Celery

Authentication:
- JWT tokens: Stateless authentication
- bcrypt: Password hashing
- OAuth2: Social login (optional)

Monitoring & Logging:
- Python logging: Structured logs
- Prometheus: Metrics collection
- Grafana: Metrics visualization
Frontend
yamlCore Framework: Next.js 14 (React 18+)
- Server-side rendering (SSR)
- Static generation for performance
- API routes for BFF pattern
- Image optimization

UI Libraries:
- Tailwind CSS: Utility-first styling
- shadcn/ui: Beautiful component library
- Framer Motion: Smooth animations
- Lucide React: Icon system

State Management:
- Zustand: Lightweight state management
- React Query: Server state & caching
- WebSocket: Real-time updates

Video Streaming:
- WebRTC: Low-latency video (P2P when possible)
- HLS.js: HTTP Live Streaming fallback
- MediaRecorder API: Client-side recording

Charts & Visualization:
- Recharts: Analytics dashboard
- D3.js: Custom visualizations
DevOps & Infrastructure
yamlContainerization:
- Docker: Application containers
- Docker Compose: Local development
- Multi-stage builds: Optimized images

Orchestration:
- Kubernetes: Production deployment (optional)
- Docker Swarm: Simpler alternative

CI/CD:
- GitHub Actions: Automated testing & deployment
- Pre-commit hooks: Code quality checks

Reverse Proxy:
- Nginx: Load balancing, SSL termination
- Caddy: Automatic HTTPS (alternative)

Monitoring:
- Sentry: Error tracking
- Prometheus + Grafana: System metrics
- Loki: Log aggregation
```

---

## 🧩 Detailed Component Breakdown {#components}

### Backend Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry
│   │
│   ├── api/                         # API Layer
│   │   ├── __init__.py
│   │   ├── deps.py                  # Dependency injection
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py          # POST /login, /register, /refresh
│   │   │   │   ├── camera.py        # GET/POST /cameras, /cameras/{id}/start
│   │   │   │   ├── alerts.py        # GET/POST/DELETE /alerts
│   │   │   │   ├── settings.py      # GET/PUT /settings
│   │   │   │   ├── gallery.py       # GET /gallery, /gallery/{id}
│   │   │   │   └── stats.py         # GET /stats/dashboard
│   │   │   └── router.py            # API router aggregation
│   │   └── websockets/
│   │       ├── __init__.py
│   │       ├── connection_manager.py # WebSocket connection pool
│   │       ├── video_stream.py      # Video streaming handler
│   │       └── events.py            # Real-time event broadcasting
│   │
│   ├── core/                        # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── config.py                # Pydantic settings
│   │   ├── security.py              # JWT, password hashing
│   │   ├── logging.py               # Structured logging setup
│   │   │
│   │   ├── services/                # Domain Services
│   │   │   ├── __init__.py
│   │   │   ├── camera_service.py    # Camera lifecycle management
│   │   │   ├── detection_service.py # YOLOv8 inference wrapper
│   │   │   ├── face_service.py      # Face recognition logic
│   │   │   ├── alert_service.py     # Alert creation & processing
│   │   │   ├── notification_service.py # Multi-channel notifications
│   │   │   ├── storage_service.py   # File/S3 operations
│   │   │   └── analytics_service.py # Statistics & reports
│   │   │
│   │   └── engine/                  # Core Detection Engine
│   │       ├── __init__.py
│   │       ├── detector.py          # Refactored YOLOv8 detector
│   │       ├── face_recognizer.py   # Refactored dlib face auth
│   │       ├── frame_processor.py   # Frame preprocessing pipeline
│   │       └── alert_manager.py     # Alert state machine
│   │
│   ├── models/                      # Data Models
│   │   ├── __init__.py
│   │   ├── domain/                  # Business entities
│   │   │   ├── user.py
│   │   │   ├── camera.py
│   │   │   ├── alert.py
│   │   │   ├── detection.py
│   │   │   └── settings.py
│   │   └── schemas/                 # Pydantic schemas (API contracts)
│   │       ├── auth.py              # LoginRequest, TokenResponse
│   │       ├── camera.py            # CameraCreate, CameraResponse
│   │       ├── alert.py             # AlertResponse, AlertFilter
│   │       └── stats.py             # DashboardStats
│   │
│   ├── db/                          # Database Layer
│   │   ├── __init__.py
│   │   ├── base.py                  # SQLAlchemy base
│   │   ├── session.py               # Database session factory
│   │   ├── repositories/            # Repository pattern
│   │   │   ├── __init__.py
│   │   │   ├── user_repo.py
│   │   │   ├── camera_repo.py
│   │   │   ├── alert_repo.py
│   │   │   └── settings_repo.py
│   │   └── models/                  # SQLAlchemy ORM models
│   │       ├── __init__.py
│   │       ├── user.py
│   │       ├── camera.py
│   │       ├── alert.py
│   │       ├── detection.py
│   │       └── audit_log.py
│   │
│   ├── tasks/                       # Background Tasks (Celery)
│   │   ├── __init__.py
│   │   ├── celery_app.py           # Celery configuration
│   │   ├── detection_task.py       # Continuous detection loop
│   │   ├── cleanup_task.py         # Old file cleanup
│   │   └── notification_task.py    # Async notifications
│   │
│   ├── integrations/                # External Services
│   │   ├── __init__.py
│   │   ├── telegram_bot.py         # Telegram API wrapper
│   │   ├── email_client.py         # SMTP email sender
│   │   ├── push_service.py         # Firebase/OneSignal
│   │   └── s3_client.py            # AWS S3/MinIO
│   │
│   ├── middleware/                  # HTTP Middleware
│   │   ├── __init__.py
│   │   ├── auth_middleware.py      # JWT validation
│   │   ├── rate_limit.py           # Rate limiting
│   │   ├── cors.py                 # CORS configuration
│   │   └── error_handler.py        # Global exception handler
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── image_utils.py          # Image processing helpers
│       ├── video_utils.py          # Video encoding/streaming
│       ├── validators.py           # Custom validators
│       └── helpers.py              # Generic helpers
│
├── tests/                           # Test Suite
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   └── e2e/                        # End-to-end tests
│
├── alembic/                         # Database Migrations
│   ├── versions/
│   └── env.py
│
├── scripts/                         # Utility Scripts
│   ├── seed_db.py                  # Database seeding
│   ├── train_faces.py              # Face recognition training
│   └── backup.py                   # Backup automation
│
├── requirements/
│   ├── base.txt                    # Core dependencies
│   ├── dev.txt                     # Development tools
│   └── prod.txt                    # Production optimizations
│
├── .env.example                     # Environment template
├── Dockerfile                       # Backend container
├── docker-compose.yml              # Development environment
├── pytest.ini                      # Pytest configuration
└── README.md
```

### Frontend Structure
```
frontend/
├── public/
│   ├── icons/
│   ├── sounds/                     # Alert sound effects
│   └── manifest.json               # PWA manifest
│
├── src/
│   ├── app/                        # Next.js 14 App Router
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Landing page
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx          # Dashboard layout
│   │   │   ├── page.tsx            # Main dashboard
│   │   │   ├── cameras/
│   │   │   │   └── page.tsx
│   │   │   ├── alerts/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── gallery/
│   │   │   │   └── page.tsx
│   │   │   ├── settings/
│   │   │   │   └── page.tsx
│   │   │   └── analytics/
│   │   │       └── page.tsx
│   │   └── api/                    # API routes (BFF pattern)
│   │       └── [...proxy]/
│   │           └── route.ts        # Proxy to backend
│   │
│   ├── components/                 # React Components
│   │   ├── ui/                     # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── toast.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   │
│   │   ├── camera/
│   │   │   ├── VideoFeed.tsx       # Real-time video component
│   │   │   ├── CameraCard.tsx
│   │   │   ├── CameraControls.tsx
│   │   │   └── CameraSettings.tsx
│   │   │
│   │   ├── alerts/
│   │   │   ├── AlertList.tsx
│   │   │   ├── AlertCard.tsx
│   │   │   ├── AlertModal.tsx
│   │   │   └── AlertTimeline.tsx
│   │   │
│   │   ├── gallery/
│   │   │   ├── ImageGrid.tsx
│   │   │   ├── ImageViewer.tsx
│   │   │   └── VideoPlayer.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── StatsCard.tsx
│   │   │   ├── ActivityChart.tsx
│   │   │   ├── DetectionHeatmap.tsx
│   │   │   └── RecentAlerts.tsx
│   │   │
│   │   └── settings/
│   │       ├── GeneralSettings.tsx
│   │       ├── NotificationSettings.tsx
│   │       ├── CameraSettings.tsx
│   │       └── UserSettings.tsx
│   │
│   ├── lib/                        # Utilities & Helpers
│   │   ├── api/                    # API Client
│   │   │   ├── client.ts           # Axios instance with interceptors
│   │   │   ├── auth.ts             # Auth endpoints
│   │   │   ├── cameras.ts          # Camera endpoints
│   │   │   ├── alerts.ts           # Alert endpoints
│   │   │   └── websocket.ts        # WebSocket client
│   │   │
│   │   ├── hooks/                  # Custom React Hooks
│   │   │   ├── useAuth.ts          # Authentication hook
│   │   │   ├── useWebSocket.ts     # WebSocket connection
│   │   │   ├── useVideoStream.ts   # Video streaming
│   │   │   ├── useAlerts.ts        # Alert management
│   │   │   ├── useCamera.ts        # Camera control
│   │   │   └── useSettings.ts      # Settings management
│   │   │
│   │   ├── stores/                 # Zustand State Management
│   │   │   ├── authStore.ts        # User authentication state
│   │   │   ├── cameraStore.ts      # Camera state
│   │   │   ├── alertStore.ts       # Alerts state
│   │   │   └── settingsStore.ts    # App settings
│   │   │
│   │   ├── utils/
│   │   │   ├── date.ts             # Date formatting
│   │   │   ├── image.ts            # Image processing
│   │   │   ├── validators.ts       # Form validation
│   │   │   └── cn.ts               # className utility
│   │   │
│   │   └── constants/
│   │       ├── routes.ts           # Route definitions
│   │       ├── config.ts           # App configuration
│   │       └── messages.ts         # UI messages
│   │
│   ├── types/                      # TypeScript Types
│   │   ├── api.ts                  # API response types
│   │   ├── camera.ts
│   │   ├── alert.ts
│   │   ├── user.ts
│   │   └── settings.ts
│   │
│   ├── styles/
│   │   ├── globals.css             # Global styles + Tailwind
│   │   └── animations.css          # Custom animations
│   │
│   └── middleware.ts               # Next.js middleware (auth)
│
├── .env.local.example
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md

🗄️ Database Schema {#database}
PostgreSQL Tables
sql-- Users Table
CREATE TABLE users (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
email VARCHAR(255) UNIQUE NOT NULL,
username VARCHAR(100) UNIQUE NOT NULL,
hashed_password VARCHAR(255) NOT NULL,
full_name VARCHAR(255),
is_active BOOLEAN DEFAULT TRUE,
is_superuser BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_login TIMESTAMP,

-- Profile
avatar_url TEXT,
phone VARCHAR(20),
notification_preferences JSONB DEFAULT '{
"email": true,
"telegram": true,
"push": true,
"alert_types": ["intruder", "motion"]
}'::jsonb
);

-- Cameras Table
CREATE TABLE cameras (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
name VARCHAR(100) NOT NULL,
location VARCHAR(255),

-- Camera Configuration
source_type VARCHAR(20) NOT NULL, -- 'webcam', 'ip', 'usb', 'rtsp'
source_url TEXT,  -- For IP/RTSP cameras
source_index INTEGER,  -- For USB/Webcam (0, 1, 2, etc.)

-- Status
is_active BOOLEAN DEFAULT FALSE,
is_armed BOOLEAN DEFAULT FALSE,
status VARCHAR(20) DEFAULT 'offline', -- 'online', 'offline', 'error'

-- Settings
resolution VARCHAR(20) DEFAULT '1280x720',
fps INTEGER DEFAULT 30,
detection_enabled BOOLEAN DEFAULT TRUE,
face_recognition_enabled BOOLEAN DEFAULT TRUE,

-- Detection Configuration
detection_config JSONB DEFAULT '{
"confidence_threshold": 0.5,
"detection_classes": ["person", "car", "animal"],
"detection_zones": [],
"sensitivity": 5
}'::jsonb,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts Table
CREATE TABLE alerts (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
camera_id UUID REFERENCES cameras(id) ON DELETE CASCADE,
user_id UUID REFERENCES users(id) ON DELETE CASCADE,

-- Alert Information
alert_type VARCHAR(50) NOT NULL, -- 'intruder', 'motion', 'face_detected', 'face_unknown'
severity VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
title VARCHAR(255) NOT NULL,
description TEXT,

-- Detection Details
detected_objects JSONB, -- Array of {class, confidence, bbox}
face_match_confidence FLOAT,
recognized_person VARCHAR(255),

-- Media
image_path TEXT,
video_path TEXT,
thumbnail_path TEXT,

-- Status
is_read BOOLEAN DEFAULT FALSE,
is_archived BOOLEAN DEFAULT FALSE,
acknowledged_at TIMESTAMP,
acknowledged_by UUID REFERENCES users(id),

-- Metadata
metadata JSONB, -- Additional context (weather, time of day, etc.)

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_camera ON alerts(camera_id);
CREATE INDEX idx_alerts_user ON alerts(user_id);
CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);

-- Detections Table (Detailed detection logs)
CREATE TABLE detections (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
camera_id UUID REFERENCES cameras(id) ON DELETE CASCADE,

-- Detection Data
class_name VARCHAR(100) NOT NULL,
confidence FLOAT NOT NULL,
bbox JSONB NOT NULL, -- {x, y, width, height}

-- Frame Information
frame_number INTEGER,
timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

-- Model Information
model_name VARCHAR(100),
model_version VARCHAR(50)
);

-- Known Faces Table
CREATE TABLE known_faces (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,

name VARCHAR(255) NOT NULL,
encoding BYTEA NOT NULL, -- dlib face encoding (serialized numpy array)

-- Training Images
training_images TEXT[], -- Array of image paths

-- Metadata
added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_seen TIMESTAMP,
times_detected INTEGER DEFAULT 0
);

-- System Settings Table
CREATE TABLE settings (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,

-- General Settings
timezone VARCHAR(50) DEFAULT 'UTC',
date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
time_format VARCHAR(20) DEFAULT 'HH:mm:ss',

-- Notification Settings
telegram_bot_token TEXT,
telegram_chat_id TEXT,
smtp_config JSONB,

-- Detection Settings
global_confidence_threshold FLOAT DEFAULT 0.5,
alert_cooldown_seconds INTEGER DEFAULT 30,
max_alerts_per_hour INTEGER DEFAULT 100,

-- Storage Settings
retention_days INTEGER DEFAULT 30,
auto_cleanup_enabled BOOLEAN DEFAULT TRUE,

-- UI Preferences
theme VARCHAR(20) DEFAULT 'dark',
dashboard_layout JSONB,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

UNIQUE(user_id)
);

-- Activity Log Table (Audit Trail)
CREATE TABLE activity_logs (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE SET NULL,

action VARCHAR(100) NOT NULL, -- 'login', 'camera_armed', 'settings_changed', etc.
resource_type VARCHAR(50), -- 'camera', 'alert', 'settings'
resource_id UUID,

details JSONB, -- Additional context
ip_address INET,
user_agent TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_user ON activity_logs(user_id);
CREATE INDEX idx_activity_created ON activity_logs(created_at DESC);

-- Statistics Table (Pre-aggregated for dashboard)
CREATE TABLE daily_statistics (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
camera_id UUID REFERENCES cameras(id) ON DELETE CASCADE,
date DATE NOT NULL,

total_detections INTEGER DEFAULT 0,
total_alerts INTEGER DEFAULT 0,
intruder_alerts INTEGER DEFAULT 0,
false_positives INTEGER DEFAULT 0,

detections_by_class JSONB, -- {"person": 45, "car": 12, ...}
hourly_distribution JSONB, -- {"00": 2, "01": 1, ..., "23": 5}

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

UNIQUE(user_id, camera_id, date)
);
Redis Data Structures
python# Session Management
session:{user_id} -> {
"token": "jwt_token",
"expires_at": timestamp,
"device_info": {...}
}
TTL: 24 hours

# Camera State (Real-time)
camera:{camera_id}:state -> {
"status": "online",
"fps": 29.8,
"armed": true,
"last_frame_time": timestamp,
"active_connections": 3
}
TTL: 5 minutes (refreshed on heartbeat)

# Alert Queue (For rate limiting)
alerts:{user_id}:recent -> [alert_id1, alert_id2, ...]
TTL: 1 hour

# WebSocket Connections
ws:connections:{user_id} -> Set of connection IDs
TTL: Session duration

# Detection Cache (Prevent duplicate alerts)
detection:{camera_id}:last -> {
"objects": [...],
"timestamp": timestamp,
"hash": "frame_hash"
}
TTL: 30 seconds

# Rate Limiting
ratelimit:{endpoint}:{user_id} -> request_count
TTL: 1 hour

🔌 API Design {#api-design}
REST API Endpoints
yaml# Authentication
POST   /api/v1/auth/register
Body: {email, username, password, full_name}
Response: {user, access_token, refresh_token}

POST   /api/v1/auth/login
Body: {username, password}
Response: {access_token, refresh_token, user}

POST   /api/v1/auth/refresh
Body: {refresh_token}
Response: {access_token}

POST   /api/v1/auth/logout
Headers: Authorization Bearer <token>
Response: {message}

GET    /api/v1/auth/me
Response: {user}

# Cameras
GET    /api/v1/cameras
Query: ?status=online&is_armed=true
Response: {cameras: [...], total: 5}

POST   /api/v1/cameras
Body: {name, location, source_type, source_url, detection_config}
Response: {camera}

GET    /api/v1/cameras/{camera_id}
Response: {camera, recent_alerts, statistics}

PUT    /api/v1/cameras/{camera_id}
Body: {name?, location?, detection_config?}
Response: {camera}

DELETE /api/v1/cameras/{camera_id}
Response: {message}

POST   /api/v1/cameras/{camera_id}/arm
Response: {camera, armed: true}

POST   /api/v1/cameras/{camera_id}/disarm
Response: {camera, armed: false}

POST   /api/v1/cameras/{camera_id}/start
Response: {camera, status: "online"}

POST   /api/v1/cameras/{camera_id}/stop
Response: {camera, status: "offline"}

GET    /api/v1/cameras/{camera_id}/snapshot
Response: Image (JPEG)

# Alerts
GET    /api/v1/alerts
Query: ?camera_id=xxx&type=intruder&severity=high&from=2025-01-01&to=2025-01-31&page=1&limit=20
Response: {alerts: [...], total, page, pages}

GET    /api/v1/alerts/{alert_id}
Response: {alert, detections: [...]}

PATCH  /api/v1/alerts/{alert_id}/read
Response: {alert}

PATCH  /api/v1/alerts/{alert_id}/archive
Response: {alert}

DELETE /api/v1/alerts/{alert_id}
Response: {message}

POST   /api/v1/alerts/{alert_id}/acknowledge
Response: {alert}

# Gallery
GET    /api/v1/gallery
Query: ?type=image&camera_id=xxx&from=2025-01-01&page=1&limit=50
Response: {media: [...], total, page}

GET    /api/v1/gallery/{media_id}
Response: Image/Video file

DELETE /api/v1/gallery/{media_id}
Response: {message}

# Settings
GET    /api/v1/settings
Response: {settings}

PUT    /api/v1/settings
Body: {timezone?, notification_preferences?, detection_settings?}
Response: {settings}

GET    /api/v1/settings/telegram/status
Response: {connected: true,Continue5:36 PMchat_id, bot_username}POST   /api/v1/settings/telegram/connect
Body: {bot_token, chat_id}
Response: {connected: true}POST   /api/v1/settings/telegram/test
Response: {sent: true, message_id}Known Faces
GET    /api/v1/faces
Response: {faces: [...]}POST   /api/v1/faces
Body: FormData {name, images: [File, File, ...]}
Response: {face}DELETE /api/v1/faces/{face_id}
Response: {message}POST   /api/v1/faces/{face_id}/train
Body: FormData {images: [File, ...]}
Response: {face, training_count}Statistics & Analytics
GET    /api/v1/stats/dashboard
Query: ?period=7d&camera_id=xxx
Response: {
total_detections,
total_alerts,
detections_by_class: {...},
alerts_by_type: {...},
hourly_distribution: [...],
daily_trend: [...],
top_cameras: [...]
}GET    /api/v1/stats/cameras/{camera_id}
Query: ?from=2025-01-01&to=2025-01-31
Response: {
uptime_percentage,
total_detections,
average_fps,
detection_timeline: [...]
}GET    /api/v1/stats/export
Query: ?format=csv&from=2025-01-01&to=2025-01-31
Response: CSV/Excel fileSystem
GET    /api/v1/system/health
Response: {status: "healthy", services: {...}, version}GET    /api/v1/system/info
Response: {version, uptime, cameras_online, alerts_today}POST   /api/v1/system/cleanup
Body: {older_than_days: 30}
Response: {deleted_files, freed_space}

### WebSocket Protocol
```javascript// Connection
ws://localhost:8000/ws/video/{camera_id}?token=<jwt_token>
ws://localhost:8000/ws/events?token=<jwt_token>// Video Stream Messages
Client -> Server:
{
"type": "subscribe",
"camera_id": "uuid"
}Server -> Client (Video Frames):
{
"type": "frame",
"camera_id": "uuid",
"timestamp": 1640000000.123,
"data": "base64_encoded_jpeg", // or binary
"fps": 29.8,
"frame_number": 12345
}// Event Stream Messages
Server -> Client (Real-time Events):
{
"type": "alert",
"data": {
"alert_id": "uuid",
"camera_id": "uuid",
"alert_type": "intruder",
"severity": "high",
"title": "Unknown person detected",
"image_url": "/api/v1/gallery/xxx",
"timestamp": "2025-01-01T10:30:00Z"
}
}{
"type": "detection",
"data": {
"camera_id": "uuid",
"objects": [
{"class": "person", "confidence": 0.95, "bbox": [100, 200, 50, 150]}
],
"timestamp": "2025-01-01T10:30:00Z"
}
}{
"type": "camera_status",
"data": {
"camera_id": "uuid",
"status": "online",
"armed": true,
"fps": 30
}
}{
"type": "system",
"data": {
"message": "Settings updated",
"level": "info"
}
}// Heartbeat
Client <-> Server:
{"type": "ping"}
{"type": "pong"}

---

## 🎨 Frontend Architecture {#frontend}

### Component HierarchyApp (Next.js Layout)
│
├── AuthProvider (Authentication Context)
│   └── LoginPage / RegisterPage
│
└── DashboardLayout (Protected Routes)
├── Navbar
│   ├── UserMenu
│   ├── NotificationBell (Real-time alerts)
│   └── ThemeToggle
│
├── Sidebar
│   ├── Navigation Links
│   └── SystemStatus
│
└── Main Content
│
├── Dashboard Page (/)
│   ├── StatsOverview (Cards: Detections, Alerts, Cameras)
│   ├── LiveCameraGrid
│   │   └── VideoFeed (WebRTC/WebSocket)
│   ├── RecentAlerts (Timeline)
│   └── ActivityChart (Recharts)
│
├── Cameras Page (/cameras)
│   ├── CameraList
│   │   └── CameraCard
│   │       ├── VideoPreview
│   │       ├── StatusIndicator
│   │       └── ControlButtons (Arm/Disarm/Start/Stop)
│   ├── AddCameraDialog
│   └── CameraDetailsModal
│
├── Alerts Page (/alerts)
│   ├── AlertFilters (Date, Type, Severity, Camera)
│   ├── AlertList (Virtualized)
│   │   └── AlertCard
│   │       ├── Thumbnail
│   │       ├── AlertInfo
│   │       └── Actions (View/Archive/Delete)
│   └── AlertDetailModal
│       ├── ImageViewer (Zoom, Pan)
│       ├── DetectionOverlay (Bounding boxes)
│       └── AlertMetadata
│
├── Gallery Page (/gallery)
│   ├── MediaFilters
│   ├── ImageGrid (Infinite scroll)
│   │   └── MediaCard
│   └── Lightbox (Full-screen viewer)
│
├── Settings Page (/settings)
│   ├── SettingsTabs
│   │   ├── GeneralSettings
│   │   ├── NotificationSettings
│   │   │   ├── TelegramSetup
│   │   │   ├── EmailSetup
│   │   │   └── PushNotifications
│   │   ├── CameraDefaults
│   │   ├── DetectionSettings
│   │   │   ├── ConfidenceSlider
│   │   │   ├── ClassSelector
│   │   │   └── ZoneDrawer (Canvas)
│   │   ├── FaceManagement
│   │   │   ├── KnownFacesList
│   │   │   └── AddFaceDialog (Image upload)
│   │   └── StorageSettings
│   └── SaveButton
│
└── Analytics Page (/analytics)
├── DateRangePicker
├── DetectionChart (Bar/Line)
├── HeatMap (Detection hotspots)
├── CameraComparison
└── ExportButton (CSV/PDF)

### State Management Strategy
```typescript// authStore.ts (Zustand)
interface AuthState {
user: User | null;
token: string | null;
isAuthenticated: boolean;
login: (username: string, password: string) => Promise<void>;
logout: () => void;
refreshToken: () => Promise<void>;
}// cameraStore.ts
interface CameraState {
cameras: Camera[];
selectedCamera: Camera | null;
fetchCameras: () => Promise<void>;
updateCamera: (id: string, data: Partial<Camera>) => Promise<void>;
armCamera: (id: string) => Promise<void>;
disarmCamera: (id: string) => Promise<void>;
}// alertStore.ts
interface AlertState {
alerts: Alert[];
unreadCount: number;
filters: AlertFilters;
fetchAlerts: (filters?: AlertFilters) => Promise<void>;
markAsRead: (id: string) => Promise<void>;
archiveAlert: (id: string) => Promise<void>;
addRealtimeAlert: (alert: Alert) => void; // Called by WebSocket
}// settingsStore.ts
interface SettingsState {
settings: AppSettings;
fetchSettings: () => Promise<void>;
updateSettings: (data: Partial<AppSettings>) => Promise<void>;
}

### Custom Hooks
```typescript// useWebSocket.ts
export function useWebSocket(url: string) {
const [isConnected, setIsConnected] = useState(false);
const [lastMessage, setLastMessage] = useState<any>(null);useEffect(() => {
const ws = new WebSocket(url);ws.onopen = () => setIsConnected(true);
ws.onmessage = (event) => setLastMessage(JSON.parse(event.data));
ws.onclose = () => setIsConnected(false);return () => ws.close();
}, [url]);const sendMessage = (message: any) => {
if (ws.readyState === WebSocket.OPEN) {
ws.send(JSON.stringify(message));
}
};return { isConnected, lastMessage, sendMessage };
}// useVideoStream.ts
export function useVideoStream(cameraId: string) {
const canvasRef = useRef<HTMLCanvasElement>(null);
const { lastMessage } = useWebSocket(ws://api.com/ws/video/${cameraId});useEffect(() => {
if (lastMessage?.type === 'frame') {
const canvas = canvasRef.current;
const ctx = canvas?.getContext('2d');
const img = new Image();  img.onload = () => {
ctx?.drawImage(img, 0, 0, canvas.width, canvas.height);
};  img.src = `data:image/jpeg;base64,${lastMessage.data}`;
}
}, [lastMessage]);return { canvasRef };
}// useAlerts.ts
export function useAlerts() {
const { alerts, fetchAlerts, addRealtimeAlert } = useAlertStore();
const { lastMessage } = useWebSocket('ws://api.com/ws/events');useEffect(() => {
fetchAlerts();
}, []);useEffect(() => {
if (lastMessage?.type === 'alert') {
addRealtimeAlert(lastMessage.data);
// Play sound
new Audio('/sounds/alert.mp3').play();
// Show toast notification
toast.error(lastMessage.data.title);
}
}, [lastMessage]);return { alerts };
}

---

## ⚡ Real-time Communication {#realtime}

### Video Streaming Architecture┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Camera    │ ──────> │   Backend   │ ──────> │   Frontend  │
│  (OpenCV)   │ frames  │  (FastAPI)  │ WebSocket│   (React)   │
└─────────────┘         └─────────────┘         └─────────────┘
│
│ Processing
▼
┌─────────────┐
│   YOLOv8    │
│  Detection  │
└─────────────┘

### Implementation Options

**Option 1: WebSocket + JPEG Streaming (Recommended for MVP)**
```pythonBackend: Stream JPEG frames over WebSocket
@router.websocket("/ws/video/{camera_id}")
async def video_stream(websocket: WebSocket, camera_id: str):
await websocket.accept()
camera = camera_service.get_camera(camera_id)while True:
frame = camera.read()    # Resize for bandwidth efficiency
frame = cv2.resize(frame, (1280, 720))    # Encode as JPEG
_, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])    # Send as base64
await websocket.send_json({
"type": "frame",
"data": base64.b64encode(buffer).decode(),
"timestamp": time.time()
})    await asyncio.sleep(1/30)  # 30 FPS
```typescript// Frontend: Render frames on canvas
const VideoFeed = ({ cameraId }: Props) => {
const canvasRef = useRef<HTMLCanvasElement>(null);
const { lastMessage } = useWebSocket(ws://api/ws/video/${cameraId});useEffect(() => {
if (lastMessage?.type === 'frame') {
const img = new Image();
img.onload = () => {
const ctx = canvasRef.current?.getContext('2d');
ctx?.drawImage(img, 0, 0);
};
img.src = data:image/jpeg;base64,${lastMessage.data};
}
}, [lastMessage]);return <canvas ref={canvasRef} width={1280} height={720} />;
};

**Option 2: WebRTC (Low Latency, More Complex)**
- Use aiortc (Python WebRTC library)
- Benefits: Lower latency (~100ms vs 500ms), less bandwidth
- Complexity: STUN/TURN servers, peer connection management

**Option 3: HLS/DASH (Scalable, Higher Latency)**
- Generate HLS playlist with FFmpeg
- Benefits: CDN distribution, adaptive bitrate
- Use case: Playback of recorded footage, not live monitoring

### Event Broadcasting
```pythonBackend: Connection Manager
class ConnectionManager:
def init(self):
self.active_connections: Dict[str, List[WebSocket]] = {}async def connect(self, user_id: str, websocket: WebSocket):
await websocket.accept()
if user_id not in self.active_connections:
self.active_connections[user_id] = []
self.active_connections[user_id].append(websocket)async def disconnect(self, user_id: str, websocket: WebSocket):
self.active_connections[user_id].remove(websocket)async def broadcast_to_user(self, user_id: str, message: dict):
if user_id in self.active_connections:
for connection in self.active_connections[user_id]:
await connection.send_json(message)manager = ConnectionManager()Send alert to all user's devices
async def notify_user(user_id: str, alert: Alert):
await manager.broadcast_to_user(user_id, {
"type": "alert",
"data": alert.dict()
})

---

## 🔐 Security & Authentication {#security}

### JWT Authentication Flow┌────────┐                   ┌────────┐                   ┌────────┐
│ Client │                   │  API   │                   │  Redis │
└───┬────┘                   └───┬────┘                   └───┬────┘
│                            │                            │
│ 1. POST /auth/login        │                            │
│ {username, password}       │                            │
├───────────────────────────>│                            │
│                            │                            │
│                            │ 2. Verify credentials      │
│                            │    (bcrypt)                │
│                            │                            │
│                            │ 3. Generate JWT            │
│                            │    (access + refresh)      │
│                            │                            │
│                            │ 4. Store refresh token     │
│                            ├───────────────────────────>│
│                            │                            │
│ 5. Return tokens           │                            │
│<───────────────────────────┤                            │
│                            │                            │
│ 6. Subsequent requests     │                            │
│ Authorization: Bearer <JWT>│                            │
├───────────────────────────>│                            │
│                            │                            │
│                            │ 7. Validate JWT            │
│                            │    (signature, expiry)     │
│                            │                            │
│ 8. Response                │                            │
│<───────────────────────────┤                            │

### Implementation
```pythoncore/security.py
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedeltapwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7def verify_password(plain_password: str, hashed_password: str) -> bool:
return pwd_context.verify(plain_password, hashed_password)def get_password_hash(password: str) -> str:
return pwd_context.hash(password)def create_access_token(data: dict) -> str:
to_encode = data.copy()
expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
to_encode.update({"exp": expire, "type": "access"})
return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)def create_refresh_token(data: dict) -> str:
to_encode = data.copy()
expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
to_encode.update({"exp": expire, "type": "refresh"})
return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)def verify_token(token: str) -> dict:
try:
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
return payload
except JWTError:
raise HTTPException(status_code=401, detail="Invalid token")api/deps.py (Dependency Injection)
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentialssecurity = HTTPBearer()async def get_current_user(
credentials: HTTPAuthorizationCredentials = Depends(security),
db: Session = Depends(get_db)
) -> User:
token = credentials.credentials
payload = verify_token(token)if payload.get("type") != "access":
raise HTTPException(status_code=401, detail="Invalid token type")user_id = payload.get("sub")
user = db.query(User).filter(User.id == user_id).first()if not user or not user.is_active:
raise HTTPException(status_code=401, detail="User not found")return user

### API Key Authentication (for programmatic access)
```pythonmodels/api_key.py
class APIKey(Base):
tablename = "api_keys"id = Column(UUID, primary_key=True, default=uuid.uuid4)
user_id = Column(UUID, ForeignKey("users.id"))
key = Column(String, unique=True, index=True)  # Hashed
name = Column(String)  # "My Automation Script"
scopes = Column(JSONB)  # ["cameras:read", "alerts:write"]
last_used = Column(DateTime)
expires_at = Column(DateTime)Usage in endpoints
async def verify_api_key(api_key: str = Header(...)):
hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
key_record = db.query(APIKey).filter(APIKey.key == hashed_key).first()if not key_record or key_record.expires_at < datetime.utcnow():
raise HTTPException(status_code=403, detail="Invalid API key")return key_record.user

---

## 🚀 Deployment Strategy {#deployment}

### Docker Configuration
```dockerfilebackend/Dockerfile
FROM python:3.11-slimWORKDIR /appInstall system dependencies
RUN apt-get update && apt-get install -y 
libgl1-mesa-glx 
libglib2.0-0 
libsm6 
libxext6 
libxrender-dev 
libgomp1 
&& rm -rf /var/lib/apt/lists/*Install Python dependencies
COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txtCopy application
COPY app/ /app/app/Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuserEXPOSE 8000CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```dockerfilefrontend/Dockerfile
FROM node:20-alpine AS builderWORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run buildFROM node:20-alpine AS runner
WORKDIR /appENV NODE_ENV productionRUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjsCOPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/staticUSER nextjs
EXPOSE 3000CMD ["node", "server.js"]

### Docker Compose (Development)
```yamlversion: '3.8'services:
postgres:
image: postgres:16-alpine
environment:
POSTGRES_DB: security_system
POSTGRES_USER: admin
POSTGRES_PASSWORD: changeme
volumes:
- postgres_data:/var/lib/postgresql/data
ports:
- "5432:5432"
healthcheck:
test: ["CMD-SHELL", "pg_isready -U admin"]
interval: 10s
timeout: 5s
retries: 5redis:
image: redis:7-alpine
ports:
- "6379:6379"
volumes:
- redis_data:/data
healthcheck:
test: ["CMD", "redis-cli", "ping"]
interval: 10s
timeout: 3s
retries: 5backend:
build:
context: ./backend
dockerfile: Dockerfile
environment:
DATABASE_URL: postgresql://admin:changeme@postgres:5432/security_system
REDIS_URL: redis://redis:6379/0
SECRET_KEY: dev-secret-key-change-in-prod
TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
volumes:
- ./backend/app:/app/app
- ./logs:/app/logs
- ./models:/app/models  # YOLOv8 weights
ports:
- "8000:8000"
depends_on:
postgres:
condition: service_healthy
redis:
condition: service_healthy
devices:
- /dev/video0:/dev/video0  # Webcam access
restart: unless-stoppedcelery-worker:
build:
context: ./backend
dockerfile: Dockerfile
command: celery -A app.tasks.celery_app worker --loglevel=info
environment:
DATABASE_URL: postgresql://admin:changeme@postgres:5432/security_system
REDIS_URL: redis://redis:6379/0
volumes:
- ./backend/app:/app/app
- ./logs:/app/logs
depends_on:
- postgres
- redis
restart: unless-stoppedcelery-beat:
build:
context: ./backend
dockerfile: Dockerfile
command: celery -A app.tasks.celery_app beat --loglevel=info
environment:
DATABASE_URL: postgresql://admin:changeme@postgres:5432/security_system
REDIS_URL: redis://redis:6379/0
depends_on:
- postgres
- redis
restart: unless-stoppedfrontend:
build:
context: ./frontend
dockerfile: Dockerfile
target: builder  # Dev stage
environment:
NEXT_PUBLIC_API_URL: http://localhost:8000
NEXT_PUBLIC_WS_URL: ws://localhost:8000
volumes:
- ./frontend:/app
- /app/node_modules
ports:
- "3000:3000"
depends_on:
- backend
restart: unless-stoppednginx:
image: nginx:alpine
volumes:
- ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
- ./nginx/ssl:/etc/nginx/ssl:ro
ports:
- "80:80"
- "443:443"
depends_on:
- backend
- frontend
restart: unless-stoppedvolumes:
postgres_data:
redis_data:

### Production Deployment (Kubernetes)
```yamlk8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
name: security-backend
spec:
replicas: 3
selector:
matchLabels:
app: security-backend
template:
metadata:
labels:
app: security-backend
spec:
containers:
- name: backend
image: your-registry/security-backend:latest
ports:
- containerPort: 8000
env:
- name: DATABASE_URL
valueFrom:
secretKeyRef:
name: db-secret
key: url
resources:
requests:
memory: "512Mi"
cpu: "500m"
limits:
memory: "2Gi"
cpu: "2000m"
livenessProbe:
httpGet:
path: /health
port: 8000
initialDelaySeconds: 30
periodSeconds: 10
readinessProbe:
httpGet:
path: /health
port: 8000
initialDelaySeconds: 5
periodSeconds: 5
apiVersion: v1
kind: Service
metadata:
name: security-backend
spec:
selector:
app: security-backend
ports:

port: 80
targetPort: 8000
type: LoadBalancer


### CI/CD Pipeline (GitHub Actions)
```yaml.github/workflows/deploy.yml
name: Deployon:
push:
branches: [main]jobs:
test:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v3  - name: Set up Python
uses: actions/setup-python@v4
with:
python-version: '3.11'  - name: Install dependencies
run: |
cd backend
pip install -r requirements/dev.txt  - name: Run tests
run: |
cd backend
pytest tests/ --cov=app --cov-report=xml  - name: Upload coverage
uses: codecov/codecov-action@v3build-backend:
needs: test
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v3  - name: Set up Docker Buildx
uses: docker/setup-buildx-action@v2  - name: Login to Container Registry
uses: docker/login-action@v2
with:
registry: ghcr.io
username: ${{ github.actor }}
password: ${{ secrets.GITHUB_TOKEN }}  - name: Build and push
uses: docker/build-push-action@v4
with:
context: ./backend
push: true
tags: ghcr.io/${{ github.repository }}/backend:latest
cache-from: type=gha
cache-to: type=gha,mode=maxbuild-frontend:
needs: test
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v3  - name: Set up Node
uses: actions/setup-node@v3
with:
node-version: '20'  - name: Build and push
uses: docker/build-push-action@v4
with:
context: ./frontend
push: true
tags: ghcr.io/${{ github.repository }}/frontend:latestdeploy:
needs: [build-backend, build-frontend]
runs-on: ubuntu-latest
steps:
- name: Deploy to production
run: |
# SSH into server and pull new images
ssh secrets.SERVERUSER@{{ secrets.SERVER_USER }}@
secrets.SERVERU​SER@{{ secrets.SERVER_HOST }}

'cd /opt/security-system && docker-compose pull && docker-compose up -d'

---

## 📊 Migration Roadmap {#migration}

### Phase 1: Backend Foundation (Week 1-2)

**Goal:** Extract logic from `main.py`, set up FastAPI structure# Build stage
FROM python:3.10-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libgl1 \
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
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user early
RUN useradd -m -u 1000 fess

# Copy Python packages from builder to a location accessible by fess
COPY --from=builder /root/.local /home/fess/.local
RUN chown -R fess:fess /home/fess/.local/

# Copy application code
COPY src/ ./src/
COPY known_faces/ ./known_faces/

# Create directories for configs and checkpoints
RUN mkdir -p ./configs ./checkpoints ./logs ./docker && \
    chown -R fess:fess /app

# Add local Python packages to PATH
ENV PATH=/home/fess/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUSERBASE=/home/fess/.local

# Copy entrypoint script
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh && \
    chown fess:fess /app/docker/entrypoint.sh

USER fess

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000

# Entry point
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["python", "-m", "src.main"]
