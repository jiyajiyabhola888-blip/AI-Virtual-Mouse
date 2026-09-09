# 🖱️ Virtual AI Mouse & Air-Writing Keyboard

> A real-time AI-powered Human-Computer Interaction system that enables users to control a computer using hand gestures and air-writing through a webcam.

---

## 📌 Overview

Virtual AI Mouse & Air-Writing Keyboard is a Computer Vision and Artificial Intelligence based desktop application that transforms hand movements into real-time computer commands without requiring a traditional mouse or keyboard.

Using a webcam, the system detects and tracks the user's hand through MediaPipe's 21 hand landmarks and interprets various finger gestures to perform actions such as:

- Cursor Movement
- Left Click
- Right Click
- Double Click
- Drag & Drop
- Screenshot Capture

In addition to gesture-based control, the project introduces an Air-Writing Keyboard, where users can write supported letters in the air using their index finger. The system analyzes the finger trajectory, recognizes the written character, and automatically launches the mapped application or website.

The entire solution operates locally on the user's machine, providing a touch-free and intuitive Human-Computer Interaction experience.

---

## 🎯 Problem Statement

Traditional computer interaction relies heavily on physical devices such as a mouse and keyboard.

This project addresses these challenges by providing:

- ✅ Touch-free computer control
- ✅ AI-based gesture interaction
- ✅ Air-writing based application launching
- ✅ Accessibility-focused user experience
- ✅ Human-Computer Interaction research platform
- ✅ Smart desktop automation using Computer Vision

---

## ⚙️ Working Principle

### 🖱️ Virtual Mouse Workflow

```text
Webcam
   ↓
Hand Detection
   ↓
21 Hand Landmark Tracking
   ↓
Gesture Recognition
   ↓
Mouse Action Execution
```

### ✍️ Air-Writing Workflow

```text
Webcam
   ↓
Hand Detection
   ↓
Air-Writing Mode
   ↓
Index Finger Trajectory
   ↓
Letter Recognition
   ↓
Application Launch
```

---

## 🧠 Core Technologies

The system combines multiple AI and Computer Vision technologies:

- MediaPipe Hand Landmark Detection
- OpenCV Image Processing
- Gesture Recognition
- Trajectory Analysis
- Template Matching
- Desktop Automation using PyAutoGUI

Using 21 hand landmarks, the system identifies:

- Finger positions
- Raised fingers
- Finger touch events
- Hand movement patterns
- Writing trajectories
- Gesture classifications

These features are converted into corresponding computer actions in real time.

---

## ✨ Features

### 🖱️ Gesture-Based Virtual Mouse

| Gesture | Action |
|----------|----------|
| ☝️ Index Finger | Cursor Movement |
| 🤏 Thumb + Index | Left Click |
| 🤏 Thumb + Middle | Right Click |
| 🤏 Thumb + Ring | Double Click |
| 🤏 Thumb + Pinky | Drag & Drop |
| 🖐️ Open Hand | Screenshot |

---

### ✍️ Air-Writing Keyboard

Activate Air-Writing mode by raising:

- Index Finger
- Middle Finger

The system tracks the index fingertip trajectory and recognizes the written character.

---

### 🔤 Supported Air-Written Commands

| Letter | Action |
|----------|----------|
| W | WhatsApp Web |
| Y | YouTube |
| G | Google |
| I | Instagram |
| C | Google Chrome |
| N | Notepad |

Example:

```text
Draw "W"
     ↓
Recognized
     ↓
WhatsApp Web Opens
```

---

### 🧩 Hybrid Letter Recognition

The recognition engine combines:

1. Trajectory Analysis
2. Template Matching

This dual-recognition approach improves accuracy and robustness compared to single-method systems.

---

### 📸 Gesture-Based Screenshot

Raise all five fingers:

```text
🖐️ → Screenshot Captured
```

Screenshots are automatically saved with timestamp-based filenames.

Example:

```text
shot_20260909_105043.png
```

---

## 🏗️ System Architecture

```text
                    ┌───────────────┐
                    │    Webcam     │
                    └───────┬───────┘
                            ↓
                  ┌───────────────────┐
                  │   Hand Tracker    │
                  │ MediaPipe + OpenCV│
                  └─────────┬─────────┘
                            ↓
                  ┌───────────────────┐
                  │ Gesture Detection │
                  └───────┬─────┬─────┘
                          ↓     ↓
                    ┌─────┘     └──────┐
                    ↓                   ↓
             ┌─────────────┐    ┌─────────────┐
             │ Virtual     │    │ Air-Writing │
             │ Mouse       │    │ Recognition │
             └──────┬──────┘    └──────┬──────┘
                    ↓                   ↓
             Mouse Actions      Letter Detection
                                        ↓
                                 Application Launcher
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core Development |
| OpenCV | Image Processing |
| MediaPipe | Hand Landmark Detection |
| cvzone | Hand Tracking Utilities |
| PyAutoGUI | Mouse Automation |
| NumPy | Numerical Processing |
| Git & GitHub | Version Control |

---

## 🚀 Future Scope

- Full A–Z Air-Writing Support
- More Gesture-Based Controls
- Custom Gesture Mapping
- Multi-Hand Interaction
- Voice + Gesture Control
- Personalized Recognition Models
- Cross-Platform Support
- Accessibility-Focused Interaction

---

## 🎓 Applications

- Human-Computer Interaction (HCI)
- Accessibility Systems
- Touch-Free Interfaces
- Smart Classrooms
- Computer Vision Research
- Desktop Automation

---

## 👩‍💻 Author

**Jiya Bhola**  
B.Tech CSE (AI/ML)

GitHub: https://github.com/jiyajiyabhola888-blip
