import cv2
import threading
import numpy as np
import os
from loguru import logger
from datetime import datetime
from typing import List, Tuple, Dict, Any

# ===== PYTORCH 2.6 COMPATIBILITY PATCH =====
import torch
import torch.serialization

# Register safe globals for YOLO models
torch.serialization.add_safe_globals([
    torch.nn.modules.container.Sequential,
    torch.nn.modules.linear.Linear,
    torch.nn.modules.activation.ReLU,
    torch.nn.modules.activation.SiLU,
    torch.nn.modules.pooling.MaxPool2d,
    torch.nn.modules.conv.Conv2d,
    torch.nn.modules.batchnorm.BatchNorm2d,
    torch.nn.modules.dropout.Dropout,
    # Ultralytics specific
    torch.serialization.DEFAULT_PROTOCOL,
])

# Monkey-patch torch.load to handle weights_only
_original_torch_load = torch.load

def patched_torch_load(f, *args, **kwargs):
    """Wrapper to load YOLO weights with weights_only=False"""
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    try:
        return _original_torch_load(f, *args, **kwargs)
    except Exception:
        # If it fails, try with weights_only=False explicitly
        kwargs['weights_only'] = False
        return _original_torch_load(f, *args, **kwargs)

torch.load = patched_torch_load
# ===== END PATCH =====

from ultralytics import YOLO
from app.core.config import settings

try:
    import face_recognition
    FACE_REC_AVAILABLE = True
    print("DEBUG: Face Recognition Library is INSTALLED and WORKING")
except ImportError:
    FACE_REC_AVAILABLE = False
    print("DEBUG: Face Recognition Library is MISSING")


class DetectionService:
    def __init__(self, model_name="yolov8n.pt"):
        self.model = None
        # Use absolute path for model
        base_path = os.getcwd()
        self.model_path = os.path.join(base_path, model_name)
        self.is_ready = False
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self._load_lock = threading.Lock()
        
        # Face Recognition
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Track identities
        self.identity_map = {} # {track_id: {'name': str, 'last_checked': int}}
        self.frame_count = 0
        self.face_check_interval = 10
        
        # ROI from settings (normalized)
        self.roi_points = [
            (0.2, 0.2), # Top-Left
            (0.8, 0.2), # Top-Right
            (0.8, 0.8), # Bottom-Right
            (0.2, 0.8)  # Bottom-Left
        ]

    def load_model(self):
        with self._load_lock:
            if self.is_ready:
                return
            
            logger.info(f"YOLO INITIALIZATION START: Loading {self.model_path}")
            try:
                logger.info(f"Checking for model at: {self.model_path}")
                self.model = YOLO(self.model_path)
                self._load_known_faces()
                self.is_ready = True
                logger.success("--- YOLO DETECTION SERVICE IS NOW READY ---")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                raise e # Propagate so we know it failed

    def _load_known_faces(self):
        if not FACE_REC_AVAILABLE:
            logger.warning("Face recognition package not found. Skipping face load.")
            return

        known_faces_path = settings.KNOWN_FACES_DIR
        if not os.path.exists(known_faces_path):
            os.makedirs(known_faces_path)
            return

        logger.info(f"Loading known faces from {known_faces_path}...")
        for filename in os.listdir(known_faces_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(known_faces_path, filename)
                try:
                    img = cv2.imread(filepath)
                    if img is None: continue
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    rgb_img = np.array(rgb_img, dtype=np.uint8)
                    encodings = face_recognition.face_encodings(rgb_img)
                    
                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        name = os.path.splitext(filename)[0].split('_')[0]
                        self.known_face_names.append(name)
                        logger.debug(f"Loaded face: {name}")
                except Exception as e:
                    logger.error(f"Error loading face {filename}: {e}")

    def identify_face(self, frame, bbox):
        if not FACE_REC_AVAILABLE or not self.known_face_encodings:
            return "Unknown"
        
        x1, y1, x2, y2 = bbox
        try:
            face_img = frame[y1:y2, x1:x2]
            if face_img.size == 0: return "Unknown"
            
            rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            rgb_face = np.array(rgb_face, dtype=np.uint8)
            face_encodings = face_recognition.face_encodings(rgb_face)
            
            if not face_encodings:
                return "Unknown"
            
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encodings[0], tolerance=0.5)
            if True in matches:
                return self.known_face_names[matches.index(True)]
            return "Unknown"
        except Exception:
            return "Unknown"

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict], str]:
        if not self.is_ready:
            logger.info("DetectionService: Model not loaded, attempting auto-load...")
            try:
                self.load_model()
            except Exception:
                return frame, [], "SAFE"

        if frame is None:
            return None, [], "SAFE"

        self.frame_count += 1
        # logger.debug(f"Processing frame {self.frame_count}")
        
        # Optimization: Use smaller imgsz for faster CPU inference
        results = self.model.track(
            frame, 
            classes=[0], 
            conf=self.confidence_threshold, 
            persist=True, 
            verbose=False,
            imgsz=480 # Increased from 320 for better quality
        )
        
        height, width = frame.shape[:2]
        detections = []
        overall_status = "SAFE"
        
        # ROI
        roi_pixel_cnt = np.array([
            (int(x * width), int(y * height)) 
            for x, y in self.roi_points
        ], dtype=np.int32)
        
        found_any = False
        for result in results:
            if result.boxes is None: continue
                
            for box in result.boxes:
                found_any = True
                cls = int(box.cls[0].cpu().numpy())
                conf = float(box.conf[0].cpu().numpy())
                logger.debug(f"Found object class {cls} with conf {conf}")
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                track_id = int(box.id[0].cpu().numpy()) if box.id is not None else -1
                conf = float(box.conf[0].cpu().numpy())
                
                # ROI Check
                center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                is_inside = cv2.pointPolygonTest(roi_pixel_cnt, center, False) >= 0
                
                name = "Unknown"
                if is_inside:
                    if track_id != -1 and track_id in self.identity_map and \
                       (self.frame_count - self.identity_map[track_id]['last_checked']) <= self.face_check_interval:
                        name = self.identity_map[track_id]['name']
                    else:
                        name = self.identify_face(frame, (x1, y1, x2, y2))
                        if track_id != -1:
                            self.identity_map[track_id] = {'name': name, 'last_checked': self.frame_count}
                
                # Status
                status = "WARNING"
                color = (0, 255, 255)
                
                if is_inside:
                    if name == "Unknown":
                        status = "CRITICAL"
                        color = (0, 0, 255)
                        overall_status = "CRITICAL"
                    else:
                        status = "AUTHORIZED"
                        color = (0, 255, 0)
                elif overall_status != "CRITICAL":
                    overall_status = "WARNING"

                detections.append({
                    "bbox": (x1, y1, x2, y2),
                    "conf": conf,
                    "status": status,
                    "name": name,
                    "is_inside": is_inside
                })
                
                # Visualization
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{status} {name if name != 'Unknown' else ''}".strip()
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if not found_any and FACE_REC_AVAILABLE:
            # Fallback: If YOLO misses a close-up person, try face detection
            try:
                rgb_small = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_small, model="hog")
                
                for top, right, bottom, left in face_locations:
                    found_any = True
                    # Create a pseudo-bbox for the "person" based on face
                    # We expand it a bit downwards to cover shoulders
                    p_x1, p_y1 = max(0, left - 50), max(0, top - 50)
                    p_x2, p_y2 = min(width, right + 50), min(height, bottom + 150)
                    
                    center = (int((p_x1 + p_x2) / 2), int((p_y1 + p_y2) / 2))
                    is_inside = cv2.pointPolygonTest(roi_pixel_cnt, center, False) >= 0
                    
                    name = self.identify_face(frame, (left, top, right, bottom))
                    status = "AUTHORIZED" if name != "Unknown" else ("CRITICAL" if is_inside else "WARNING")
                    if status == "CRITICAL": overall_status = "CRITICAL"
                    elif overall_status != "CRITICAL": overall_status = "WARNING"
                    
                    detections.append({
                        "bbox": (p_x1, p_y1, p_x2, p_y2),
                        "conf": 0.9,
                        "status": status,
                        "name": name,
                        "is_inside": is_inside
                    })
            except Exception as e:
                logger.error(f"Face fallback error: {e}")

        return frame, detections, overall_status


# Global instance
detection_service = DetectionService()
