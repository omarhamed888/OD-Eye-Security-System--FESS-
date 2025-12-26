from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    MOTION_DETECTED = "motion.detected"
    FACE_RECOGNIZED = "face.recognized"
    ALERT_TRIGGERED = "alert.triggered"
    SYSTEM_STATUS = "system.status"

class BoundingBox(BaseModel):
    """Bounding box coordinates."""
    x1: float
    y1: float
    x2: float
    y2: float
    
class DetectionEvent(BaseModel):
    """Base detection event."""
    event_id: str
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    camera_id: str
    frame_number: int
    
class MotionDetectionEvent(DetectionEvent):
    """Motion detection event."""
    event_type: EventType = EventType.MOTION_DETECTED
    detected_objects: List[dict]  # List of detections
    total_objects: int
    confidence_scores: List[float]
    
class FaceRecognitionEvent(DetectionEvent):
    """Face recognition event."""
    event_type: EventType = EventType.FACE_RECOGNIZED
    face_id: str
    person_name: Optional[str] = None
    confidence: float
    bbox: BoundingBox
    is_authorized: bool = False
    
class AlertEvent(BaseModel):
    """Alert event."""
    event_id: str
    event_type: EventType = EventType.ALERT_TRIGGERED
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    camera_id: str
    alert_level: str  # "INFO", "WARNING", "CRITICAL"
    alert_message: str
    associated_events: List[str] = []  # Related event IDs
