# 🖱️ Virtual AI Mouse & Air-Writing Keyboard

An AI-powered, webcam-based desktop control system that allows users to control a computer using **hand gestures** instead of a physical mouse.

The project also includes an **Air-Writing feature**, where users can draw letters in the air using their index finger. The system recognizes the letter and automatically opens the application mapped to it.

Built using **Python, OpenCV, MediaPipe, cvzone, PyAutoGUI, and NumPy**.

---

## 💡 What Does This Project Do?

The system uses a webcam to detect the user's hand and track finger movements in real time.

It allows users to:

- Move the mouse cursor using hand gestures
- Perform left click, right click and double click
- Drag and drop using hand gestures
- Write letters in the air
- Recognize air-written letters
- Open applications automatically using recognized letters
- Take screenshots using an open-hand gesture

---

## ⚙️ How It Works

**Webcam → Hand Detection → Finger Tracking → Gesture Recognition → Computer Action**

For Air-Writing:

**Webcam → Hand Tracking → Finger Movement → Letter Recognition → Application Launch**

The system detects **21 hand landmarks** using MediaPipe. Based on the position and movement of the fingers, it identifies the user's gesture and performs the corresponding action.

For Air-Writing, the movement of the index finger is recorded as a path. The path is analyzed and compared with predefined letter patterns to recognize the written letter.

---

## 🌟 Key Features

### 🖐️ Virtual Mouse

| Gesture | Action |
|---|---|
| Index Finger | Move Cursor |
| Thumb + Index | Left Click |
| Thumb + Middle | Right Click |
| Thumb + Ring | Double Click |
| Thumb + Pinky | Drag & Drop |

### ✍️ Air-Writing

Raise **Index + Middle fingers** to activate Air-Writing mode.

Draw a supported letter in the air using your index finger.

| Letter | Action |
|---|---|
| W | Open WhatsApp Web |
| Y | Open YouTube |
| G | Open Google |
| I | Open Instagram |
| C | Open Google Chrome |
| N | Open Windows Notepad |

After the writing is completed, the system recognizes the letter and automatically performs the mapped action.

### 📸 Screenshot

Raise all five fingers with an **Open Hand** gesture.

The system captures a screenshot and saves it with a timestamp.

---

## 🧠 Letter Recognition

The Air-Writing recognition system uses:

- **Trajectory/Path Analysis** to analyze the movement and shape of the written letter.
- **Template Matching** to compare the generated writing with reference letter templates.

Both results are combined to select the most likely letter.

---

## 🛠️ Technologies Used

- **Python** — Core programming
- **OpenCV** — Webcam and image processing
- **MediaPipe** — Hand landmark detection
- **cvzone** — Hand tracking utilities
- **PyAutoGUI** — Mouse and computer control
- **NumPy** — Mathematical calculations
- **Git & GitHub** — Version control

---

## 📁 Project Structure

```text
AI-Virtual-Mouse/
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── hand_tracker.py
│   ├── mouse_controller.py
│   ├── air_writer.py
│   ├── recognizer.py
│   ├── app_launcher.py
│   └── camera_preview.py
│
├── templates/
│   ├── W.png
│   ├── Y.png
│   ├── G.png
│   ├── I.png
│   ├── C.png
│   └── N.png
│
├── models/
├── hand_landmarker.task
├── requirements.txt
├── test_system.py
├── run.bat
└── README.md
🚀 Installation & Setup
Requirements
Windows 10 / 11
Python 3.10–3.12 recommended
Working webcam
Install Dependencies
pip install -r requirements.txt
Run the Application
python -m src.main
Or simply run:
run.bat
🧪 Testing
Run the automated test suite:
python test_system.py
The tests verify the main system components and letter recognition functionality.
🎯 Project Goal
The goal of this project is to provide a touch-free and natural way to interact with a computer using Computer Vision and hand gestures.
It combines:
Computer Vision + Hand Tracking + Gesture Recognition + Air-Writing + Computer Automation
into a single desktop application.
🔮 Future Improvements
Full A–Z Air-Writing support
More customizable gestures
Multi-hand support
Voice + gesture control
Improved letter recognition
Custom application mapping
Cross-platform support
👩‍💻 Author
Jiya Bhola
B.Tech CSE — AI/ML
GitHub: https://github.com/jiyajiyabhola888-blip⁠�
