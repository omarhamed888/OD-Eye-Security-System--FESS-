from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json
from pydantic import BaseModel
from datetime import datetime

from app.db import get_db, Alert, Camera
from app.core import security

router = APIRouter()


class AlertOut(BaseModel):
    id: str
    camera_id: str
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    face_match_confidence: Optional[float] = None
    recognized_person: Optional[str] = None
    image_path: Optional[str] = None
    is_read: bool
    created_at: datetime
    
    # These are stored as JSON strings in SQLite, need manual conversion
    detected_objects: Optional[Any] = None
    meta_data: Optional[Any] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AlertOut])
def list_alerts(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(security.get_current_token_payload),
    limit: int = 100,
    camera_id: Optional[str] = None
) -> Any:
    """
    Retrieve alerts.
    """
    user_id = token_payload.get("sub")
    
    query = db.query(Alert).filter(Alert.user_id == user_id)
    
    if camera_id:
        query = query.filter(Alert.camera_id == camera_id)
        
    alerts = query.order_by(desc(Alert.created_at)).limit(limit).all()
    
    # Process JSON strings to objects
    for alert in alerts:
        if isinstance(alert.detected_objects, str) and alert.detected_objects:
            alert.detected_objects = json.loads(alert.detected_objects)
        if isinstance(alert.meta_data, str) and alert.meta_data:
            alert.meta_data = json.loads(alert.meta_data)
            
    return alerts


@router.patch("/{alert_id}/read", response_model=AlertOut)
def mark_as_read(
    alert_id: str,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(security.get_current_token_payload)
) -> Any:
    """
    Mark an alert as read.
    """
    user_id = token_payload.get("sub")
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    
    # Process JSON strings for output
    if isinstance(alert.detected_objects, str) and alert.detected_objects:
        alert.detected_objects = json.loads(alert.detected_objects)
    if isinstance(alert.meta_data, str) and alert.meta_data:
        alert.meta_data = json.loads(alert.meta_data)
        
    return alert
