from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text
from datetime import datetime
import uuid
import json

from app.db.base import Base


class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Basic info
    name = Column(String(100), nullable=False)
    location = Column(String(255))
    
    # Camera source configuration
    source_type = Column(String(20), nullable=False)  # 'webcam', 'ip', 'usb', 'rtsp'
    source_url = Column(String, nullable=True)  # For IP/RTSP cameras
    source_index = Column(Integer, nullable=True)  # For USB/Webcam (0, 1, 2, etc.)
    
    # Status
    is_active = Column(Boolean, default=False)
    is_armed = Column(Boolean, default=False)
    status = Column(String(20), default='offline')  # 'online', 'offline', 'error'
    
    # Settings
    resolution = Column(String(20), default='1280x720')
    fps = Column(Integer, default=30)
    detection_enabled = Column(Boolean, default=True)
    face_recognition_enabled = Column(Boolean, default=True)
    
    # Detection configuration stored as JSON text
    detection_config = Column(
        Text,
        default=json.dumps({
            "confidence_threshold": 0.5,
            "detection_classes": ["person", "car", "animal"],
            "detection_zones": [],
            "sensitivity": 5
        })
    )
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Camera {self.name} ({self.status})>"
