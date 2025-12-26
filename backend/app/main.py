from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.base import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup: Create tables
    print("🚀 Starting Falcon Eye Security System API...")
    print(f"📊 Database: {settings.DATABASE_URL}")
    
    # Create tables (for development - in production use Alembic)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
    
    yield
    
    # Shutdown
    print("👋 Shutting down API...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered security monitoring with face recognition and real-time alerts",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Falcon Eye Security System API",
        "version": settings.VERSION,
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": settings.VERSION
    }


# Include routers
from app.api.v1.router import api_router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Static files for alert captures
from fastapi.staticfiles import StaticFiles
import os

captures_path = os.path.join(os.getcwd(), "logs", "captures")
if not os.path.exists(captures_path):
    os.makedirs(captures_path)
app.mount("/captures", StaticFiles(directory=captures_path), name="captures")
