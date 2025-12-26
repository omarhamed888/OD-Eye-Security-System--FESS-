from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
from pydantic import BaseModel

from app import schemas
from app.db import get_db, Camera, User
from app.core import security

router = APIRouter()


class CameraBase(BaseModel):
    name: str
    location: Optional[str] = None
    source_type: str
    source_url: Optional[str] = None
    source_index: Optional[int] = None
    resolution: Optional[str] = "1280x720"
    fps: Optional[int] = 30
    detection_enabled: Optional[bool] = True
    face_recognition_enabled: Optional[bool] = True
    detection_config: Optional[dict] = None


class CameraCreate(CameraBase):
    pass


class CameraUpdate(CameraBase):
    name: Optional[str] = None
    source_type: Optional[str] = None


class CameraOut(CameraBase):
    id: str
    user_id: str
    is_active: bool
    is_armed: bool
    status: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CameraOut])
def list_cameras(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(security.get_current_token_payload)
) -> Any:
    """
    Retrieve cameras.
    """
    user_id = token_payload.get("sub")
    cameras = db.query(Camera).filter(Camera.user_id == user_id).all()
    
    # Process detection_config from JSON string to dict
    for cam in cameras:
        if isinstance(cam.detection_config, str):
            cam.detection_config = json.loads(cam.detection_config)
            
    return cameras


@router.post("/", response_model=CameraOut)
def create_camera(
    *,
    db: Session = Depends(get_db),
    camera_in: CameraCreate,
    token_payload: dict = Depends(security.get_current_token_payload)
) -> Any:
    """
    Create new camera.
    """
    user_id = token_payload.get("sub")
    
    db_obj = Camera(
        user_id=user_id,
        name=camera_in.name,
        location=camera_in.location,
        source_type=camera_in.source_type,
        source_url=camera_in.source_url,
        source_index=camera_in.source_index,
        resolution=camera_in.resolution,
        fps=camera_in.fps,
        detection_enabled=camera_in.detection_enabled,
        face_recognition_enabled=camera_in.face_recognition_enabled,
        detection_config=json.dumps(camera_in.detection_config) if camera_in.detection_config else json.dumps({
            "confidence_threshold": 0.5,
            "detection_classes": ["person", "car", "animal"],
            "detection_zones": [],
            "sensitivity": 5
        })
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    if isinstance(db_obj.detection_config, str):
        db_obj.detection_config = json.loads(db_obj.detection_config)
        
    return db_obj
