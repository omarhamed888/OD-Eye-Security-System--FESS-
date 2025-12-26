# 🎨 Frontend Interface & User Experience

![Dashboard UI Concept](./assets/ui_concept.png)

## 🌌 The "Command Center" Aesthetic
The FESS interface is designed to emulate a high-tech tactical HUD (Heads-Up Display). It prioritizes immediate situational awareness through motion, color, and depth.

### Key Design Principles
1.  **Glassmorphism**: Using transparent, blurred "glass" cards to create hierarchy without losing sight of the underlying environment.
2.  **Visual DNA**: A "Neural" color palette using **Deep Cobalt (#0A0F1E)** backgrounds and **Neon Cyan (#00F2FF)** accents.
3.  **Haptic Feedback**: Every action—from arming a camera to receiving a breach notification—is accompanied by micro-animations and status transitions.

---

## 🛡️ Core Components

### 1. Optical Sensor Viewport
The primary live video feed.
*   **Bounding Boxes**: Real-time overlays around detected intruders.
*   **REC Indicator**: Pulsing red indicator when the system is actively monitoring.
*   **Scanner Overlay**: Subtle horizontal scanner lines to reinforce the AI processing aesthetic.

### 2. Combat HUD (Live Alerts)
The right-hand panel that never sleeps.
*   **Infinite Stream**: Alerts slide in from the right as they are broadcast.
*   **Severity Glow**: 
    *   🔴 **Critical**: High-intensity red glow for unauthorized persons.
    *   🟠 **Warning**: Steady orange for motion or unknown objects.
*   **HD Evidence**: Instant thumbnails of the detection event for quick verification.

### 3. Neural Metrics (Stats)
Holographic cards showing system health.
*   **Active Nodes**: Number of online camera sensors.
*   **Neutralized Threats**: Total alerts handled.
*   **Grid Stability**: Connection health of the localized network.

---

## 📱 Mobile Responsiveness
The dashboard uses a CSS Grid system that collapses the tactical overview into a single-column "Security Pager" view, ensuring the Command Center is accessible even on the move.
