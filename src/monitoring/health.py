from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime
import psutil

from ..cache.redis_cache import RedisCache
from ..events.kafka_producer import KafkaEventProducer
from ..utils.logger import setup_logger
from ..config.settings import settings

logger = setup_logger(__name__, settings.log_level)

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthChecker:
    """System health checker."""
    
    def __init__(
        self,
        redis_client: Optional[RedisCache] = None,
        kafka_producer: Optional[KafkaEventProducer] = None
    ):
        """
        Initialize health checker.
        
        Args:
            redis_client: Redis client for health checks
            kafka_producer: Kafka producer for health checks
        """
        self.redis = redis_client
        self.kafka = kafka_producer
    
    def check_redis(self) -> Dict[str, Any]:
        """Check Redis health."""
        if not self.redis:
            return {"status": "not_configured", "healthy": True}
        
        try:
            self.redis.client.ping()
            return {
                "status": "healthy",
                "healthy": True,
                "latency_ms": 0  # Could measure actual latency
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": str(e)
            }
    
    def check_kafka(self) -> Dict[str, Any]:
        """Check Kafka health."""
        if not self.kafka:
            return {"status": "not_configured", "healthy": True}
        
        try:
            # Check if producer is connected
            metadata = self.kafka.producer.bootstrap_connected()
            return {
                "status": "healthy" if metadata else "unhealthy",
                "healthy": bool(metadata)
            }
        except Exception as e:
            logger.error(f"Kafka health check failed: {e}")
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": str(e)
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy",
                "healthy": True,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 ** 3)
            }
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {
                "status": "error",
                "healthy": False,
                "error": str(e)
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status.
        
        Returns:
            Health status dict with all component statuses
        """
        redis_health = self.check_redis()
        kafka_health = self.check_kafka()
        system_health = self.check_system_resources()
        
        # Determine overall status
        all_healthy = (
            redis_health.get("healthy", True) and
            kafka_health.get("healthy", True) and
            system_health.get("healthy", True)
        )
        
        overall_status = HealthStatus.HEALTHY if all_healthy else HealthStatus.DEGRADED
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "redis": redis_health,
                "kafka": kafka_health,
                "system": system_health
            }
        }
