import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Logging Configuration
logger.remove() # Remove default handler
logger.add(sys.stderr, level="INFO")
logger.add(LOGS_DIR / "fess.log", rotation="10 MB", retention="10 days", level="DEBUG")

# Environment Variables Validation
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CAMERA_INDEX = os.getenv("CAMERA_INDEX", "0")

# Convert CAMERA_INDEX to int if it's a digit, otherwise keep as string (for file paths)
if CAMERA_INDEX.isdigit():
    CAMERA_INDEX = int(CAMERA_INDEX)

if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "your_token_here":
    logger.warning("TELEGRAM_TOKEN is missing or invalid in .env. Telegram notifications will be disabled.")

if not CHAT_ID or CHAT_ID == "your_chat_id_here":
    logger.warning("CHAT_ID is missing or invalid in .env. Alerts cannot be sent.")

# Detection Config
CONFIDENCE_THRESHOLD = 0.6
ALERT_COOLDOWN = 30  # Seconds
MODEL_PATH = "yolov8n.pt" 

# ROI Config (Normalized 0-1: x, y)
# Default: A central rectangular area
ROI_POINTS = [
    (0.2, 0.2), # Top-Left
    (0.8, 0.2), # Top-Right
    (0.8, 0.8), # Bottom-Right
    (0.2, 0.8)  # Bottom-Left
]
