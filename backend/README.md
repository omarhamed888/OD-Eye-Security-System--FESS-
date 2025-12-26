# Backend Quick Start Guide

## 🚀 Quick Start

### 1. Start Databases
```bash
# From project root
docker-compose up -d
```

### 2. Activate Virtual Environment
```bash
cd backend
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 3. Copy Environment Variables
```bash
# Edit backend/.env with your settings (already created from .env.example)
```

### 4. Run the API
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **Root**: http://localhost:8000

## 📦 What's Been Created

### Backend Structure
```
backend/
├── app/
│   ├── core/          # Configuration & security
│   ├── db/            # Database models & session
│   ├── api/           # (To be added: API endpoints)
│   └── main.py        # FastAPI application
├── requirements/
│   ├── base.txt       # Core dependencies
│   └── dev.txt        # Development tools
└── .env               # Environment configuration
```

### Database Models
- **User**: Authentication and user profiles
- **Camera**: Camera configuration and status
- **Alert**: Security alerts and detections

### Services Running
- PostgreSQL on port 5432
- Redis on port 6379

## ⚡ Next Steps

We'll continue with:
1. ✅ Basic API structure created
2. 🔄 Add authentication endpoints (next)
3. ⏳ Camera management endpoints
4. ⏳ Extract detection logic from main.py
