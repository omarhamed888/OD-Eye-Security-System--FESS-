import cv2
import time
import threading
import queue
from datetime import datetime
from src.config import CAMERA_INDEX, ALERT_COOLDOWN, LOGS_DIR, ROI_POINTS, logger
from src.detector import ObjectDetector
from src.notifier import TelegramBot

class ThreadedCamera:
    """
    Reads frames in a separate thread to prevent I/O blocking.
    """
    def __init__(self, src=0):
        self.src = src
        self.capture = cv2.VideoCapture(src)
        self.q = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()

    def _reader(self):
        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                # If reading from a file, loop it? Or stop?
                # For security cam, we might want to retry.
                # For now, just break.
                break
            
            # Keep queue size small to ensure real-time processing
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get() if not self.q.empty() else None

    def release(self):
        self.running = False
        self.capture.release()

def main():
    logger.info("Starting Falcon Eye Security System (FESS)...")

    # 1. Initialize Components
    bot = TelegramBot()
    bot.start()
    
    try:
        detector = ObjectDetector()
    except Exception:
        logger.critical("Failed to initialize Detector. Exiting.")
        return

    # 2. Start Camera
    logger.info(f"Connecting to camera source: {CAMERA_INDEX}")
    camera = ThreadedCamera(CAMERA_INDEX)
    
    # Allow camera to warm up
    time.sleep(2.0)
    
    last_alert_time = 0
    
    logger.info("System Ready. Press 'q' to exit.")

    try:
        while True:
            frame = camera.read()
            if frame is None:
                # If camera is slow, wait a bit
                time.sleep(0.01)
                continue

            # 3. Process Frame
            processed_frame, detections, status = detector.detect_frame(frame, ROI_POINTS)
            
            # 4. Alert Logic
            current_time = time.time()
            
            # Check if we need to alert
            if bot.is_armed and status == "CRITICAL":
                if (current_time - last_alert_time) > ALERT_COOLDOWN:
                    logger.warning("CRITICAL SECURITY BREACH DETECTED!")
                    
                    # Save Evidence
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"alert_{timestamp}.jpg"
                    filepath = LOGS_DIR / filename
                    cv2.imwrite(str(filepath), processed_frame)
                    
                    # Send Notification
                    msg = f"🚨 INTRUDER DETECTED 🚨\nTime: {timestamp}\nStatus: CRITICAL"
                    bot.send_alert(str(filepath), msg)
                    
                    last_alert_time = current_time
            
            # 5. Display Interface
            # Overlay System Status
            status_color = (0, 255, 0) if bot.is_armed else (0, 0, 255)
            status_text = "ARMED" if bot.is_armed else "DISARMED"
            cv2.putText(processed_frame, f"System: {status_text}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            cv2.imshow("FESS - Monitor", processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        logger.info("User interrupted system.")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    finally:
        bot.running = False
        camera.release()
        cv2.destroyAllWindows()
        logger.info("System Shutdown Complete.")

if __name__ == "__main__":
    main()
