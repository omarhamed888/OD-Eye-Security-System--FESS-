from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Text
from datetime import datetime
import uuid

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    camera_id = Column(String(36), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Alert information
    alert_type = Column(String(50), nullable=False)  # 'intruder', 'motion', 'face_detected', 'face_unknown'
    severity = Column(String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    
    # Detection details
    detected_objects = Column(Text, nullable=True)  # JSON array of {class, confidence, bbox}
    face_match_confidence = Column(Float, nullable=True)
    recognized_person = Column(String(255), nullable=True)
    
    # Media paths
    image_path = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Additional metadata (stored as JSON text for SQLite)
    meta_data = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Alert {self.alert_type} - {self.severity}>"
