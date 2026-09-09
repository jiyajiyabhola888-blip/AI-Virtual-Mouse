# Virtual AI Mouse & Keyboard

A complete, polished, real-time webcam-based **Virtual Mouse & Air-Writing Keyboard** desktop application for Windows built using Python 3.12, OpenCV, MediaPipe, cvzone, PyAutoGUI, and NumPy.

The system empowers users to navigate and control their entire operating system using natural hand gestures and draw letters in the air using their index finger to automatically launch web applications and desktop tools.

---

## 🌟 Key Features

- **Real-Time 21-Landmark Hand Tracking**: High-precision hand pose and finger extension detection using MediaPipe and cvzone.
- **Ultra-Smooth Virtual Mouse**: Exponential moving average (EMA) interpolation eliminates cursor jitter while screen boundary padding allows effortless reach to all monitor corners.
- **Intuitive Gesture Controls**:
  - **Index Only**: Move Cursor
  - **Thumb + Index Pinch**: Left Click (debounced)
  - **Thumb + Middle Pinch**: Right Click (debounced)
  - **Thumb + Ring Pinch**: Double Click (debounced)
  - **Thumb + Pinky Pinch**: Drag & Drop (hold & release)
- **Air-Writing Mode (`[0, 1, 1, 0, 0]`)**:
  - Activated by raising Index + Middle fingers together.
  - Draws anti-aliased glowing neon strokes directly on the camera canvas.
  - Automatically isolates writing from mouse clicks to eliminate gesture conflicts.
- **Dual-Mode Letter Recognition Engine**:
  - **Trajectory / Path Analysis (88% weight)**: Resamples polylines into 64 equidistant points, normalizes aspect ratios, and evaluates Euclidean distances and tangent direction vectors against canonical mathematical stroke models.
  - **Template Image Matching (12% weight)**: Compares rendered strokes against template images using normalized cross-correlation and IoU.
  - **Guaranteed Positive Scoring**: Mathematically calibrated scores ensure path scores are never 0.000.
  - **Easy Recognition Mode**: Automatically picks the highest-scoring candidate among `W`, `Y`, `G`, `I`, `C`, `N` once writing completes.
- **Automated App Launcher**:
  - `W` ➔ **WhatsApp Web** (`https://web.whatsapp.com/`)
  - `Y` ➔ **YouTube** (`https://www.youtube.com/`)
  - `G` ➔ **Google Search** (`https://www.google.com/`)
  - `I` ➔ **Instagram** (`https://www.instagram.com/`)
  - `C` ➔ **Google Chrome** (executes local Chrome binary if found; falls back safely to browser)
  - `N` ➔ **Windows Notepad** (`notepad.exe`)
- **Open-Hand Screenshot Tool (`[1, 1, 1, 1, 1]`)**:
  - Raising all 5 fingers captures a high-resolution screenshot.
  - Auto-saved with timestamp to `screenshots/shot_YYYYMMDD_HHMMSS.png` with anti-spam cooldown.
- **Polished Glassmorphic HUD**:
  - Live mode badges (`MOUSE`, `AIR WRITING`, `SCREENSHOT`, `IDLE`).
  - Active finger telemetry display (`[T, I, M, R, P]`).
  - Real-time recognition metrics and mapped application feedback.
  - Visual gesture cheatsheet and floating toast alerts.

---

## 📁 Project Structure

```
virtual_ai_mouse_keyboard/
│
├── src/
│   ├── __init__.py            # Package initialization & path resolver
│   ├── main.py                # Main application loop & gesture prioritization
│   ├── config.py              # Central configurations, thresholds, and mappings
│   ├── hand_tracker.py        # 21-landmark tracking & finger status engine
│   ├── mouse_controller.py    # Coordinate mapping, smoothing & gesture clicks
│   ├── air_writer.py          # Trajectory collection & glowing stroke rendering
│   ├── recognizer.py          # Dual trajectory + template letter recognizer
│   ├── app_launcher.py        # Safe Windows application & URL execution
│   └── camera_preview.py      # Glassmorphic HUD overlay & telemetry renderer
│
├── templates/                 # Binary template reference images
│   ├── W.png
│   ├── Y.png
│   ├── G.png
│   ├── I.png
│   ├── C.png
│   └── N.png
│
├── screenshots/               # Directory where captured screenshots are saved
├── models/                    # Directory for models and weights
│
├── test_system.py             # Automated unit & synthetic recognition test suite
├── requirements.txt           # Python package dependencies
├── run.bat                    # Windows one-click batch launcher
└── README.md                  # Complete documentation
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Operating System**: Windows 10 / 11
- **Python**: Python 3.10 to 3.12 (Tested on Python 3.12.10)
- **Webcam**: Standard USB or built-in webcam

### Step 1: Clone or Open Project Directory
Open PowerShell or Command Prompt in the project folder:
```bash
cd c:\Users\HP\OneDrive\Desktop\mouse
```

### Step 2: Install Dependencies
Install all required libraries using `pip`:
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Option 1: Using Python Module (Recommended)
Run the application from the project root:
```bash
python -m src.main
```

### Option 2: Using the Windows Batch File
Double-click `run.bat` or execute in terminal:
```cmd
run.bat
```

### Option 3: Direct Script Launch
```bash
python src/main.py
```

---

## 🖐️ Gesture Control Reference

| Gesture | Finger State | Action | Description |
| :--- | :---: | :--- | :--- |
| **Index Only** | `[0, 1, 0, 0, 0]` | **Move Cursor** | Moves the mouse cursor smoothly across the screen. |
| **Thumb + Index** | Pinch Tips | **Left Click** | Triggers single left mouse click (debounced). |
| **Thumb + Middle** | Pinch Tips | **Right Click** | Triggers context menu / right click (debounced). |
| **Thumb + Ring** | Pinch Tips | **Double Click** | Opens files / folders with double click. |
| **Thumb + Pinky** | Pinch Tips | **Drag & Drop** | Holds mouse button down while moving; release to drop. |
| **Index + Middle** | `[0, 1, 1, 0, 0]` | **Air-Writing** | Draws strokes on screen with Index finger. |
| **Open Hand** | `[1, 1, 1, 1, 1]` | **Screenshot** | Captures screen and saves to `screenshots/`. |

---

## ✍️ Air-Writing & Letter Recognition Guide

1. **Activate Writing**: Raise your **Index and Middle fingers** together (`[0, 1, 1, 0, 0]`).
2. **Draw Letter**: Move your Index fingertip in the air to draw any of the 6 supported letters:
   - **`W`** ➔ Draw standard 'W' stroke ➔ Opens **WhatsApp Web**
   - **`Y`** ➔ Draw 'Y' stroke ➔ Opens **YouTube**
   - **`G`** ➔ Draw curved 'G' with inward bar ➔ Opens **Google Search**
   - **`I`** ➔ Draw top-to-bottom vertical line ➔ Opens **Instagram**
   - **`C`** ➔ Draw open curve 'C' ➔ Opens **Google Chrome**
   - **`N`** ➔ Draw 3-stroke 'N' ➔ Opens **Windows Notepad**
3. **Finish & Execute**: Simply lower your fingers or close your hand. The system immediately:
   - Evaluates the normalized trajectory against reference models.
   - Computes weighted scores across all 6 letters.
   - Logs the score breakdown to the console.
   - Launches the recognized application automatically.
   - Clears the canvas and returns to mouse mode.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| :---: | :--- |
| **`Q`** or **`ESC`** | Cleanly shuts down the application and releases camera. |
| **`C`** | Clears the air-writing canvas manually. |
| **`S`** | Manages manual screenshot capture. |

---

## 🧪 Running Automated Tests

A comprehensive test suite is included to verify recognizer accuracy, trajectory mathematics, template existence, and component lifecycles:

```bash
python test_system.py
```

Output:
```
--- Running Synthetic Letter Recognition Test ---
Target: W -> Predicted: W (Score: 0.895, path=0.908, img=0.802)
Target: Y -> Predicted: Y (Score: 0.867, path=0.914, img=0.521)
Target: G -> Predicted: G (Score: 0.826, path=0.875, img=0.469)
Target: I -> Predicted: I (Score: 0.957, path=0.990, img=0.718)
Target: C -> Predicted: C (Score: 0.833, path=0.891, img=0.412)
Target: N -> Predicted: N (Score: 0.800, path=0.834, img=0.550)
----------------------------------------------------------------------
Ran 6 tests in 0.490s - OK
```

---

## 🔧 Troubleshooting & Tips

- **Webcam Lighting**: Ensure adequate lighting so hand landmarks are detected sharply without blur.
- **Air-Writing Tip**: Keep your hand facing the camera and write letters at moderate speed for crisp trajectory sampling.
- **Camera Selection**: If you have multiple webcams, change `CAMERA_ID = 0` in `src/config.py` to `1` or `2`.
- **Screen Margin Reach**: If you want a wider or narrower active region for mouse control, adjust `FRAME_REDUCTION_X` and `FRAME_REDUCTION_Y` in `src/config.py`.
- **Failsafe**: PyAutoGUI failsafe is safely disabled so moving the cursor to the screen corners will never throw an exception.
