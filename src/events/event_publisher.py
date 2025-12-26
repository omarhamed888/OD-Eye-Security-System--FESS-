from typing import Optional, List
from datetime import datetime
import uuid

from .kafka_producer import KafkaEventProducer
from .event_schemas import (
    MotionDetectionEvent,
    FaceRecognitionEvent,
    AlertEvent,
    BoundingBox
)
from ..config.settings import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__, settings.log_level)

class EventPublisher:
    """High-level event publisher for FESS events."""
    
    def __init__(self, kafka_producer: Optional[KafkaEventProducer] = None):
        """
        Initialize event publisher.
        
        Args:
            kafka_producer: Kafka producer instance
        """
        self.kafka = kafka_producer or KafkaEventProducer()
    
    def publish_motion_event(
        self,
        camera_id: str,
        frame_number: int,
        detected_objects: List[dict],
        confidence_scores: List[float]
    ) -> bool:
        """
        Publish motion detection event.
        
        Args:
            camera_id: Camera identifier
            frame_number: Frame number
            detected_objects: List of detected objects
            confidence_scores: Confidence scores
            
        Returns:
            True if published successfully
        """
        try:
            event = MotionDetectionEvent(
                event_id=str(uuid.uuid4()),
                camera_id=camera_id,
                frame_number=frame_number,
                detected_objects=detected_objects,
                total_objects=len(detected_objects),
                confidence_scores=confidence_scores
            )
            
            return self.kafka.send_event(
                topic=settings.kafka.topic_motion_events,
                event=event.model_dump(),
                key=camera_id
            )
            
        except Exception as e:
            logger.error(f"Failed to publish motion event: {e}")
            return False
    
    def publish_face_event(
        self,
        camera_id: str,
        frame_number: int,
        face_id: str,
        bbox: tuple,
        confidence: float,
        person_name: Optional[str] = None,
        is_authorized: bool = False
    ) -> bool:
        """Publish face recognition event."""
        try:
            event = FaceRecognitionEvent(
                event_id=str(uuid.uuid4()),
                camera_id=camera_id,
                frame_number=frame_number,
                face_id=face_id,
                person_name=person_name,
                confidence=confidence,
                bbox=BoundingBox(x1=bbox[0], y1=bbox[1], x2=bbox[2], y2=bbox[3]),
                is_authorized=is_authorized
            )
            
            return self.kafka.send_event(
                topic=settings.kafka.topic_face_events,
                event=event.model_dump(),
                key=camera_id
            )
            
        except Exception as e:
            logger.error(f"Failed to publish face event: {e}")
            return False
    
    def publish_alert(
        self,
        camera_id: str,
        alert_level: str,
        message: str,
        associated_event_ids: List[str] = []
    ) -> bool:
        """Publish alert event."""
        try:
            event = AlertEvent(
                event_id=str(uuid.uuid4()),
                camera_id=camera_id,
                alert_level=alert_level,
                alert_message=message,
                associated_events=associated_event_ids
            )
            
            return self.kafka.send_event(
                topic=settings.kafka.topic_alert_events,
                event=event.model_dump(),
                key=camera_id
            )
            
        except Exception as e:
            logger.error(f"Failed to publish alert: {e}")
            return False
    
    def close(self) -> None:
        """Close the publisher."""
        self.kafka.close()
