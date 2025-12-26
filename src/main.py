"""
FESS Main Application Entry Point
"""
import asyncio
from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse
import uvicorn

from src.config.settings import settings
from src.monitoring.health import HealthChecker
from src.monitoring import metrics
from src.cache.redis_cache import RedisCache
from src.events.kafka_producer import KafkaEventProducer
from src.utils.logger import setup_logger

logger = setup_logger(__name__, settings.log_level)

# Initialize FastAPI app
app = FastAPI(
    title="FESS - Falcon Eye Security System",
    description="Production-Grade Motion Detection with RTMDet",
    version="1.0.0"
)

# Global components
redis_client = None
kafka_producer = None
health_checker = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global redis_client, kafka_producer, health_checker
    
    logger.info("🚀 Starting FESS Application...")
    
    try:
        # Initialize Redis
        logger.info("Initializing Redis client...")
        redis_client = RedisCache()
        logger.info("✅ Redis client initialized")
        
        # Initialize Kafka
        logger.info("Initializing Kafka producer...")
        kafka_producer = KafkaEventProducer()
        logger.info("✅ Kafka producer initialized")
        
        # Initialize Health Checker
        health_checker = HealthChecker(
            redis_client=redis_client,
            kafka_producer=kafka_producer
        )
        logger.info("✅ Health checker initialized")
        
        logger.info("🎉 FESS Application started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to start FESS: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global redis_client, kafka_producer
    
    logger.info("🛑 Shutting down FESS Application...")
    
    try:
        if kafka_producer:
            kafka_producer.close()
            logger.info("✅ Kafka producer closed")
        
        if redis_client:
            redis_client.close()
            logger.info("✅ Redis client closed")
        
        logger.info("👋 FESS Application shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "FESS - Falcon Eye Security System",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    if health_checker is None:
        return JSONResponse(
            status_code=503,
            content={"status": "initializing", "message": "Health checker not ready"}
        )
    
    try:
        status = health_checker.get_health_status()
        
        # Return 503 if unhealthy
        if status.get("status") == "unhealthy":
            return JSONResponse(status_code=503, content=status)
        
        return JSONResponse(status_code=200, content=status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": str(e)}
        )


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    try:
        metrics_data = metrics.get_metrics()
        content_type = metrics.get_content_type()
        return Response(content=metrics_data, media_type=content_type)
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        return Response(content=f"Error: {str(e)}", status_code=500)


@app.get("/info")
async def info():
    """System information endpoint."""
    return {
        "application": "FESS",
        "version": "1.0.0",
        "environment": settings.environment,
        "log_level": settings.log_level,
        "components": {
            "redis": {
                "host": settings.redis.host,
                "port": settings.redis.port,
                "db": settings.redis.db
            },
            "kafka": {
                "bootstrap_servers": settings.kafka.bootstrap_servers,
                "topics": {
                    "motion": settings.kafka.topic_motion_events,
                    "faces": settings.kafka.topic_face_events,
                    "alerts": settings.kafka.topic_alert_events
                }
            },
            "detector": {
                "device": settings.detector.device,
                "score_threshold": settings.detector.score_threshold
            }
        }
    }


def main():
    """Main entry point."""
    logger.info(f"Starting FESS on port 8000...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log Level: {settings.log_level}")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
