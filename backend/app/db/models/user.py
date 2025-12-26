from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text
from datetime import datetime
import uuid
import json

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Profile
    avatar_url = Column(String, nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Notification preferences (stored as JSON text for SQLite compatibility)
    notification_preferences = Column(
        Text,
        default=json.dumps({
            "email": True,
            "telegram": True,
            "push": True,
            "alert_types": ["intruder", "motion"]
        })
    )
    
    def __repr__(self):
        return f"<User {self.username}>"
