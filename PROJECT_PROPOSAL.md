# 🎓 Project Proposal: Falcon Eye Security System (FESS)

**Course:** Computer vision & pattern Recognition
**Team:** Falcons

---

## 1. 📄 Abstract
The **Falcon Eye Security System (FESS)** is an intelligent, automated surveillance solution designed to enhance premise security through real-time computer vision. Unlike traditional passive CCTV systems which require constant human monitoring, FESS actively monitors a video feed to detect human presence, verifies identity using Face Recognition, and instantly notifies the owner via a Telegram Bot if an unauthorized intruder enters a restricted area. This project aims to demonstrate the practical application of AI and IoT in modern security.

## 2. ❓ Problem Statement
Traditional security systems suffer from two main issues:
1.  **Passive Recording**: They only record evidence *after* a crime has occurred, rather than preventing it.
2.  **False Alarms**: Motion-based sensors trigger on pets, shadows, or moving objects, leading to alert fatigue.
3.  **High Latency**: Owners are often notified too late to take action.

## 3. 💡 Proposed Solution
FESS addresses these problems by implementing a "Smart Guard" approach:
*   **Active Detection**: Uses **YOLOv8** to specifically detect *humans*, ignoring other motion.
*   **Identity Verification**: Uses **Face Recognition** to filter out authorized personnel (Staff/Family) from actual intruders.
*   **Instant Notification**: Sends a high-priority alert with photographic evidence to the owner's smartphone via **Telegram** within seconds.
*   **Deterrence**: Triggers a local sound alarm to scare off intruders immediately.

## 4. 🛠️ Technical Architecture

### 4.1. Core Technologies
*   **Language**: Python 3.10+
*   **Computer Vision**: Ultralytics YOLOv8 (Object Detection), Dlib (Face Recognition), OpenCV (Image Processing).
*   **GUI Framework**: CustomTkinter (Modern, Dark-themed User Interface).
*   **IoT/Communication**: Python Telegram Bot (Asynchronous).
*   **Concurrency**: Multi-threading for non-blocking video capture and API calls.

### 4.2. System Flow
1.  **Input**: Webcam captures live video feed.
2.  **Processing**:
    *   Frame is analyzed by YOLOv8 for "Person" class.
    *   If a person is detected inside the ROI (Region of Interest), Face Recognition is triggered.
    *   Identity is matched against a local database of "Known Faces".
3.  **Decision**:
    *   **Authorized**: Log event, draw Green Box.
    *   **Unknown**: Trigger "CRITICAL" status, draw Red Box.
4.  **Action**:
    *   **GUI**: Update live feed, play siren sound, record video clip.
    *   **Network**: Send photo and warning text to Telegram Chat.

## 5. 👥 Team Roles & Responsibilities

This project was developed collaboratively by two members, with distinct areas of focus to ensure a robust and well-integrated system.

### **Member 1: Omar Hamed - 412200261**
**Role: AI & Computer Vision Engineer**
*   **Object Detection**: Implemented the YOLOv8 inference pipeline and optimized it for real-time performance on CPU.
*   **Face Recognition**: Developed the biometric authentication logic using `dlib` and `face_recognition`, including the "Known Faces" database management.
*   **Logic Design**: Designed the "Region of Interest" (ROI) algorithm and the state machine for "Safe/Warning/Critical" status transitions.
*   **Data Handling**: Managed image preprocessing and coordinate mapping for the visual overlays.

### **Member 2: Abdelrahman Eldaba - 412200228**
**Role: System Architect & Full-Stack Developer**
*   **GUI Development**: Built the professional Dashboard using `customtkinter`, including the Gallery, Settings panel, and real-time video rendering.
*   **IoT Integration**: Developed the asynchronous Telegram Bot for remote alerts and command-based control (`/arm`, `/disarm`).
*   **System Core**: Implemented the multi-threaded architecture (`ThreadedCamera`) to ensure the GUI remains responsive during heavy AI processing.
*   **Features**: Implemented the Sound Alarm, Video Recording, and Event Logging systems.

## 6. 📅 Expected Outcomes
A fully functional, standalone desktop application that:
1.  Connects to a standard webcam.
2.  Detects intruders with >90% accuracy.
3.  Sends alerts with <2 seconds latency.
4.  Provides a user-friendly interface for security management.

---
*Supervised by: Eng: Sohila Lashien*
