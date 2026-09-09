"""
Configuration module for Virtual AI Mouse & Keyboard.
Holds all system parameters, thresholds, timeouts, and paths.
"""
import os
import sys
import ctypes
from pathlib import Path
import pyautogui

# --------------------------------------------------
# PATHS
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SRC_DIR = PROJECT_ROOT / "src"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
MODELS_DIR = PROJECT_ROOT / "models"

# Ensure runtime directories exist
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# CAMERA SETTINGS
# --------------------------------------------------
CAMERA_ID = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FLIP_HORIZONTAL = True
FPS_TARGET = 30
WINDOW_TITLE = "Virtual AI Mouse & Keyboard"

# --------------------------------------------------
# HAND TRACKING SETTINGS
# --------------------------------------------------
MAX_HANDS = 1
DETECTION_CONFIDENCE = 0.60
TRACKING_CONFIDENCE = 0.55

# --------------------------------------------------
# VIRTUAL MOUSE SETTINGS
# --------------------------------------------------
# Detect native Windows screen resolution
try:
    SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
    SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)
    if SCREEN_WIDTH <= 0 or SCREEN_HEIGHT <= 0:
        SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
except Exception:
    try:
        SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
    except Exception:
        SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

# Boundary padding inside camera frame for screen mapping (margins)
FRAME_REDUCTION_X = 100
FRAME_REDUCTION_Y = 80

# Dynamic / Velocity-Adaptive Cursor Smoothing parameters
# Fast movements: alpha scales up to CURSOR_EMA_ALPHA_MAX (instant follow, 0 lag)
# Slow movements: alpha scales down to CURSOR_EMA_ALPHA_MIN (rock-solid, zero jitter)
CURSOR_EMA_ALPHA = 0.65
CURSOR_EMA_ALPHA_MIN = 0.28
CURSOR_EMA_ALPHA_MAX = 0.92
CURSOR_SPEED_THRESHOLD = 45.0
CURSOR_DEADZONE = 1.5

# Adaptive Pinch distance ratio (distance / hand_scale)
# hand_scale is distance from wrist (0) to middle MCP (9)
PINCH_RATIO_THRESHOLD = 0.30
DRAG_PINCH_RATIO_THRESHOLD = 0.32

# Absolute pixel fallback distance
CLICK_DISTANCE_THRESHOLD = 40
DRAG_DISTANCE_THRESHOLD = 45

# Cooldown timers (seconds)
CLICK_COOLDOWN = 0.30
DOUBLE_CLICK_COOLDOWN = 0.50
SCREENSHOT_COOLDOWN = 2.5
RECOGNITION_COOLDOWN = 1.2

# --------------------------------------------------
# AIR-WRITING SETTINGS
# --------------------------------------------------
# Gesture to write: Index and Middle UP, Ring and Pinky DOWN
AIR_WRITING_LANDMARK = 8  # Index fingertip

STROKE_COLOR = (0, 235, 255)       # Neon Yellow/Gold in BGR
STROKE_GLOW_COLOR = (0, 120, 255)  # Glow color
STROKE_THICKNESS = 6
STROKE_GLOW_THICKNESS = 14

MIN_DRAWING_POINTS = 10
WRITING_INACTIVITY_TIMEOUT = 0.8  # Seconds of no writing to finalize drawing

# --------------------------------------------------
# LETTER RECOGNITION SETTINGS
# --------------------------------------------------
SUPPORTED_LETTERS = ["W", "Y", "G", "I", "C", "N"]

TRAJECTORY_WEIGHT = 0.88
IMAGE_WEIGHT = 0.12

RESAMPLE_POINTS = 64
CANVAS_SIZE = 128

# --------------------------------------------------
# APP LAUNCHER MAPPINGS
# --------------------------------------------------
APP_MAPPINGS = {
    "W": {
        "name": "WhatsApp Web",
        "type": "url",
        "target": "https://web.whatsapp.com/"
    },
    "Y": {
        "name": "YouTube",
        "type": "url",
        "target": "https://www.youtube.com/"
    },
    "G": {
        "name": "Google",
        "type": "url",
        "target": "https://www.google.com/"
    },
    "I": {
        "name": "Instagram",
        "type": "url",
        "target": "https://www.instagram.com/"
    },
    "C": {
        "name": "Google Chrome",
        "type": "browser",
        "target": "https://www.google.com"
    },
    "N": {
        "name": "Notepad",
        "type": "app",
        "target": "notepad.exe"
    }
}

# Chrome executable search candidates on Windows
CHROME_CANDIDATE_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
]

# --------------------------------------------------
# UI / HUD COLORS & CONSTANTS (BGR)
# --------------------------------------------------
COLOR_BG_DARK = (20, 20, 24)
COLOR_CARD_BG = (35, 35, 42)
COLOR_TEXT_PRIMARY = (255, 255, 255)
COLOR_TEXT_MUTED = (175, 175, 185)
COLOR_ACCENT_CYAN = (255, 220, 0)
COLOR_ACCENT_GREEN = (80, 225, 100)
COLOR_ACCENT_ORANGE = (30, 140, 255)
COLOR_ACCENT_PURPLE = (220, 80, 200)
COLOR_ACCENT_RED = (60, 60, 240)
COLOR_BORDER = (70, 70, 85)
