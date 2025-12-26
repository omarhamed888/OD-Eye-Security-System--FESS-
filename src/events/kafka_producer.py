from typing import Optional, Dict, Any, List
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
from datetime import datetime

from ..config.settings import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__, settings.log_level)

class KafkaEventProducer:
    """Production-ready Kafka producer with error handling."""
    
    def __init__(self, bootstrap_servers: Optional[List[str]] = None):
        """
        Initialize Kafka producer.
        
        Args:
            bootstrap_servers: List of Kafka brokers
        """
        self.bootstrap_servers = bootstrap_servers or settings.kafka.bootstrap_servers
        
        producer_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'acks': settings.kafka.acks,
            'compression_type': settings.kafka.compression_type,
            'linger_ms': settings.kafka.linger_ms,
            'batch_size': settings.kafka.batch_size,
            'max_request_size': settings.kafka.max_request_size,
            'value_serializer': lambda v: json.dumps(
                v,
                default=str  # Handle datetime serialization
            ).encode('utf-8'),
            'key_serializer': lambda k: k.encode('utf-8') if k else None
        }
        
        # Add security if configured
        if settings.kafka.security_protocol != "PLAINTEXT":
            producer_config.update({
                'security_protocol': settings.kafka.security_protocol,
                'sasl_mechanism': settings.kafka.sasl_mechanism,
                'sasl_plain_username': settings.kafka.sasl_username,
                'sasl_plain_password': settings.kafka.sasl_password
            })
        
        try:
            self.producer = KafkaProducer(**producer_config)
            logger.info(f"Kafka producer initialized: {self.bootstrap_servers}")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise
    
    def send_event(
        self,
        topic: str,
        event: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """
        Send event to Kafka topic.
        
        Args:
            topic: Kafka topic name
            event: Event data (dict)
            key: Optional partition key
            
        Returns:
            True if sent successfully
        """
        try:
            future = self.producer.send(topic, value=event, key=key)
            
            # Wait for acknowledgment (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                f"Event sent to {topic} "
                f"(partition {record_metadata.partition}, "
                f"offset {record_metadata.offset})"
            )
            
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send event to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending event: {e}")
            return False
    
    def flush(self, timeout: Optional[int] = None) -> None:
        """Flush pending messages."""
        try:
            self.producer.flush(timeout=timeout)
            logger.debug("Kafka producer flushed")
        except Exception as e:
            logger.error(f"Error flushing Kafka producer: {e}")
    
    def close(self) -> None:
        """Close the producer."""
        try:
            self.producer.close()
            logger.info("Kafka producer closed")
        except Exception as e:
            logger.error(f"Error closing Kafka producer: {e}")
