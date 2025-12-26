# Data Flow & Lifecycle of an Alert

![Data Flow](../data_flow_process_1766784736761.png)

## 📡 The Alert Journey
Below is the step-by-step technical flow of how a detection becomes a HUD notification.

### Step 1: Optical Intake
*   The `CameraService` captures frames from the available optical sensor (Webcam/IP Camera).
*   Frames are converted to the internal processing format (RGB).

### Step 2: Neural Processing
*   The frame is passed into `DetectionService`.
*   **Object Detection**: YOLO identifies "person", "dog", "car", etc., with confidence scores.
*   **Biometrics**: If a person is detected, the Face ID engine checks for known identities in the database.
*   **Result**: A detection object is created with bounding boxes and classification.

### Step 3: Persistence & Triggering
*   If a threat is confirmed (e.g., person in a restricted ROI), `CameraService` triggers `_handle_alert`.
*   **DB Save**: The alert is saved to the database with a link to the camera and current timestamp.
*   **Storage**: A high-definition snapshot of the breach is saved to `backend/logs/captures`.

### Step 4: System-Wide Broadcast
*   The `AlertManager` broadcasts the alert payload to all active WebSocket subscribers.
*   The `NotificationService` sends an urgent message + image to the configured Telegram chat.

### Step 5: Combat HUD Display
*   The Next.js Frontend receives the WebSocket packet.
*   The **Combat HUD** state updates instantly, sliding a new alert card into the view.
*   System status shifts from `SAFE` (Green) to `CRITICAL` (Red) with an automated reset timer.
