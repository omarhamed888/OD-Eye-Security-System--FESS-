import cv2
import threading
import queue
import time
from loguru import logger
import asyncio
from typing import Optional
from datetime import datetime
import os
import numpy as np

from app.core.services.detection_service import detection_service
from app.core.services.notification_service import notification_service
from app.core.config import settings


class CameraService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CameraService, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, src=0):
        if self._initialized:
            return
        
        self.src = src
        self.capture = None
        self.frame_queue = queue.Queue(maxsize=1)
        self.is_running = False
        self.thread = None
        
        # Security state
        self.is_armed = True
        self.last_alert_time = 0
        self.alert_cooldown = settings.ALERT_COOLDOWN
        
        self._initialized = True
        logger.info(f"CameraService initialized with src={src}")

    def start(self):
        if self.is_running:
            return
        
        # Windows optimization: CAP_DSHOW is often more stable than MF
        logger.info(f"Opening camera {self.src} using CAP_DSHOW...")
        self.capture = cv2.VideoCapture(self.src + cv2.CAP_DSHOW)
        
        if not self.capture.isOpened():
            logger.warning(f"CAP_DSHOW failed, trying default...")
            self.capture = cv2.VideoCapture(self.src)

        if not self.capture.isOpened():
            logger.error(f"Could not open camera source {self.src}")
            return False
            
        # Initialize detection model in background to avoid blocking main loop
        threading.Thread(target=detection_service.load_model, daemon=True).start()
        
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        logger.info("Camera capture thread started")
        return True

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.capture:
            self.capture.release()
        logger.info("Camera capture thread stopped")

    def _recover_camera(self):
        """Attempts to re-open the camera if the stream is lost."""
        logger.warning("Attempting camera recovery...")
        if self.capture:
            self.capture.release()
        
        time.sleep(1.0)
        self.capture = cv2.VideoCapture(self.src + cv2.CAP_DSHOW)
        if not self.capture.isOpened():
            self.capture = cv2.VideoCapture(self.src)
        
        return self.capture.isOpened()

    def _capture_loop(self):
        # We use a separate state to track the latest detections
        self.current_detections = []
        self.current_status = "SAFE"
        self.detection_in_progress = False
        consecutive_failures = 0

        while self.is_running:
            try:
                ret, frame = self.capture.read()
                if not ret:
                    consecutive_failures += 1
                    logger.warning(f"Failed to read frame (fail {consecutive_failures})")
                    
                    if consecutive_failures > 10:
                        if self._recover_camera():
                            consecutive_failures = 0
                        else:
                            time.sleep(2.0)
                    else:
                        time.sleep(0.1)
                    continue
                
                consecutive_failures = 0
                # We start a detection only if one isn't already running
                # This ensures the stream stays at 30 FPS even if detection is slow
                if not self.detection_in_progress:
                    self.detection_in_progress = True
                    threading.Thread(target=self._run_detection, args=(frame.copy(),), daemon=True).start()

                # --- DRAWING LOGIC ---
                # Draw the LATEST KNOWN detections on the FRESH frame
                display_frame = self._draw_overlays(frame.copy())
                
                # --- ALERT LOGIC ---
                if self.is_armed and self.current_status == "CRITICAL":
                    current_time = time.time()
                    if current_time - self.last_alert_time > self.alert_cooldown:
                        self.last_alert_time = current_time
                        logger.warning(f"!!! SECURITY ALERT !!! - Status is {self.current_status}")
                        self._handle_alert(display_frame, self.current_detections)
                    else:
                        # logger.debug(f"Alert cooled down. Remaining: {int(self.alert_cooldown - (current_time - self.last_alert_time))}s")
                        pass
                elif self.current_status == "CRITICAL":
                    # logger.debug("System CRITICAL but DISARMED")
                    pass
                
                # Update frame queue (Non-blocking)
                if not self.frame_queue.empty():
                    try: self.frame_queue.get_nowait()
                    except queue.Empty: pass
                self.frame_queue.put(display_frame)

            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                time.sleep(1)

    def _run_detection(self, frame):
        try:
            logger.debug("Starting detection pass...")
            # We don't need the processed_frame here because we draw ourselves
            _, detections, status = detection_service.process_frame(frame)
            if detections:
                logger.info(f"Detection Success: Found {len(detections)} people. Status: {status}")
            self.current_detections = detections
            self.current_status = status
        except Exception as e:
            logger.error(f"Detection Error: {e}")
        finally:
            self.detection_in_progress = False

    def _draw_overlays(self, frame):
        """Draws current detections and ROI on a frame."""
        # Preparation
        height, width = frame.shape[:2]
        roi_pixel_cnt = np.array([(int(x * width), int(y * height)) for x, y in detection_service.roi_points], dtype=np.int32)
        
        # 1. Draw ROI
        cv2.polylines(frame, [roi_pixel_cnt], isClosed=True, color=(255, 0, 0), thickness=2)
        
        # 2. Draw Detections
        for det in self.current_detections:
            x1, y1, x2, y2 = det["bbox"]
            color = (0, 0, 255) if det["status"] == "CRITICAL" else (0, 255, 255)
            if det["status"] == "AUTHORIZED": color = (0, 255, 0)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"{det['status']} {det['name'] if det['name'] != 'Unknown' else ''}".strip()
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
        return frame

    def _handle_alert(self, frame, detections):
        """Saves alert image, saves to DB, and sends notifications."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alert_{timestamp}.jpg"
        
        # Ensure directory exists
        captures_dir = os.path.join("logs", "captures")
        if not os.path.exists(captures_dir):
            os.makedirs(captures_dir)
            
        filepath = os.path.join(captures_dir, filename)
        cv2.imwrite(filepath, frame)
        
        alert_msg = "Intruder detected in restricted area!"
        time_str = datetime.now().strftime('%H:%M:%S')
        
        # Alert data for broadcasting
        alert_data = {
            "id": f"alert_{int(time.time()*1000)}",
            "title": "Security Breach",
            "description": alert_msg,
            "severity": "high",
            "created_at": datetime.now().isoformat(),
            "image_path": f"/captures/{filename}",
            "is_read": False
        }

        # 1. Broadcast live via AlertManager
        from app.core.services.alert_manager import alert_manager
        loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_async_tasks, args=(loop, alert_data, filepath)).start()

    def _run_async_tasks(self, loop, alert_data, filepath):
        asyncio.set_event_loop(loop)
        
        # Prepare Telegram message
        tg_message = f"🚨 *SECURITY ALERT!* 🚨\n\n{alert_data['description']}\nTime: {datetime.now().strftime('%H:%M:%S')}"
        
        # Save to DB first to get a real ID if possible
        alert_id = self._save_alert_to_db(alert_data)
        if alert_id:
            alert_data["id"] = alert_id

        tasks = [
            notification_service.send_telegram_alert(tg_message, filepath),
            alert_manager.broadcast(alert_data)
        ]
        
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

    def _save_alert_to_db(self, alert_data):
        """Saves alert to the database using SessionLocal."""
        from app.db.base import SessionLocal
        from app.db.models.alert import Alert
        from app.db.models.camera import Camera
        from app.db.models.user import User
        import json

        db = SessionLocal()
        try:
            # Try to find a default user and camera
            user = db.query(User).first()
            camera = db.query(Camera).filter(Camera.index == self.src).first()
            
            if not user or not camera:
                logger.warning("DB: Missing User or Camera record for alert. Alert saved with dummy IDs.")
                user_id = user.id if user else "system_user"
                camera_id = camera.id if camera else "system_camera"
            else:
                user_id = user.id
                camera_id = camera.id

            new_alert = Alert(
                camera_id=camera_id,
                user_id=user_id,
                alert_type="intruder",
                severity=alert_data["severity"],
                title=alert_data["title"],
                description=alert_data["description"],
                image_path=alert_data["image_path"],
                detected_objects=json.dumps(alert_data.get("detections", []))
            )
            db.add(new_alert)
            db.commit()
            db.refresh(new_alert)
            logger.info(f"Alert saved to DB with ID: {new_alert.id}")
            return new_alert.id
        except Exception as e:
            logger.error(f"Error saving alert to DB: {e}")
            return None
        finally:
            db.close()

    def get_frame(self):
        try:
            return self.frame_queue.get(timeout=0.5)
        except queue.Empty:
            return None

    async def get_jpeg_frame(self):
        frame = self.get_frame()
        if frame is None:
            return None
            
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            return None
        return buffer.tobytes()

# Global instance
camera_service = CameraService()
