# 🖱️ Virtual AI Mouse & Air-Writing Keyboard

> A real-time computer interaction system that uses **hand gestures and air-writing** to control a Windows computer through a webcam.

## 📌 Overview

Virtual AI Mouse & Air-Writing Keyboard is a **Computer Vision based desktop application** that replaces traditional mouse interactions with natural hand gestures.

The system uses a webcam to detect and track the user's hand in real time. Based on finger positions and gestures, it converts hand movements into computer actions such as **cursor movement, clicking, double-clicking, right-clicking, and drag-and-drop**.

The project also introduces an **Air-Writing mechanism**. Users can raise their Index and Middle fingers, draw a supported letter in the air using the Index finger, and the system recognizes the letter and automatically performs the corresponding action.

The complete system works locally on the user's computer without requiring a separate hardware controller.

---

## 🎯 What Problem Does It Solve?

Traditional computer interaction depends mainly on physical input devices such as a mouse and keyboard.

This project explores a **touch-free Human-Computer Interaction (HCI)** approach where a webcam and hand gestures can be used as an alternative input method.

It can be useful for:

- Touch-free computer interaction
- Accessibility-focused interfaces
- Human-Computer Interaction research
- Computer Vision applications
- Gesture-controlled desktop automation
- Experimental AI-based input systems

---

## ⚙️ System Workflow

### Virtual Mouse

```text
Webcam
   ↓
Hand Detection
   ↓
21 Hand Landmark Tracking
   ↓
Finger State / Gesture Detection
   ↓
Gesture Classification
   ↓
Mouse Action
Air-Writing
Webcam
   ↓
Hand Detection
   ↓
Air-Writing Mode
   ↓
Index Finger Trajectory
   ↓
Trajectory Processing
   ↓
Letter Recognition
   ↓
Application Mapping
   ↓
Application Launch
🧠 Core Technology
The system detects the user's hand using MediaPipe hand landmarks.
A hand is represented using 21 landmark points, which provide the positions of important parts of the hand and fingers.
These landmark positions are used to determine:
Which fingers are raised
Which fingers are touching
Finger movement
Hand position
Gesture type
Air-writing trajectory
The recognized gesture is then passed to the appropriate controller to perform the required computer action.
✨ Features
1. 🖱️ Gesture-Based Virtual Mouse
The application provides complete basic mouse interaction through hand gestures.
Gesture
Function
☝️ Index Finger
Move Cursor
🤏 Thumb + Index
Left Click
🤏 Thumb + Middle
Right Click
🤏 Thumb + Ring
Double Click
🤏 Thumb + Pinky
Drag & Drop
Cursor movement is mapped from the camera frame to the computer screen and smoothed to reduce unwanted cursor movement and jitter.
2. ✍️ Air-Writing
Air-Writing allows the user to write letters without touching a keyboard.
Activation
Raise:
Index Finger + Middle Finger
This activates Air-Writing mode.
The system then tracks the movement of the Index fingertip and stores it as a trajectory.
When the writing gesture ends, the collected trajectory is processed and sent to the recognition system.
3. 🔤 Air-Written Letter Recognition
The current system supports six letters:
Letter
Mapped Action
W
WhatsApp Web
Y
YouTube
G
Google
I
Instagram
C
Google Chrome
N
Windows Notepad
For example:
Draw "W"
     ↓
Letter Recognition
     ↓
W detected
     ↓
WhatsApp Web opens
4. 🧩 Dual Recognition Approach
The letter recognition system combines two different approaches.
Trajectory / Path Analysis
The movement of the Index finger is analyzed based on its:
Shape
Direction
Position
Scale
Movement pattern
The trajectory is normalized and compared with predefined letter patterns.
Template Matching
The drawn stroke is also compared with stored reference templates for the supported letters.
The results from both methods are combined to determine the most likely recognized letter.
This makes the recognition system more robust than relying on only one matching technique.
5. 📸 Gesture-Based Screenshot
An Open Hand gesture is used to capture a screenshot.
Gesture
All five fingers raised
🖐️ → Screenshot
The screenshot is automatically saved with a timestamp.
Example:
shot_20260909_105043.png
Screenshot files are excluded from Git tracking using .gitignore.
6. 🎨 Real-Time Visual Interface
The application provides a real-time visual interface that displays:
Current operating mode
Hand tracking
Finger states
Air-writing strokes
Recognition information
Gesture feedback
Application launch status
This makes the system easier to operate and understand while running.
🏗️ Project Architecture
                    ┌───────────────┐
                    │    Webcam     │
                    └───────┬───────┘
                            ↓
                  ┌───────────────────┐
                  │   Hand Tracker    │
                  │  MediaPipe +      │
                  │     cvzone        │
                  └─────────┬─────────┘
                            ↓
                  ┌───────────────────┐
                  │ Gesture Detection │
                  └───────┬─────┬─────┘
                          ↓     ↓
                    ┌─────┘     └──────┐
                    ↓                   ↓
             ┌─────────────┐    ┌─────────────┐
             │ Virtual      │    │ Air-Writing │
             │ Mouse        │    │ Recognition │
             └──────┬──────┘    └──────┬──────┘
                    ↓                   ↓
             Mouse Actions       Letter Detection
                                        ↓
                                 Application Launcher
📁 Project Structure
AI-Virtual-Mouse/
│
├── src/
│   ├── main.py              # Main application and gesture flow
│   ├── config.py            # System configuration and thresholds
│   ├── hand_tracker.py      # Hand and finger tracking
│   ├── mouse_controller.py  # Cursor and mouse interactions
│   ├── air_writer.py        # Air-writing trajectory handling
│   ├── recognizer.py        # Letter recognition engine
│   ├── app_launcher.py      # Application and URL launching
│   ├── camera_preview.py    # Real-time visual interface
│   └── __init__.py
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
├── .gitignore
└── README.md
🛠️ Tech Stack
Technology
Role
Python
Core application development
OpenCV
Webcam capture and image processing
MediaPipe
Real-time hand landmark detection
cvzone
Hand tracking utilities
PyAutoGUI
Mouse and desktop automation
NumPy
Numerical and trajectory processing
Git & GitHub
Version control and project management
🚀 Installation
Requirements
Windows 10 / 11
Python 3.10–3.12 recommended
Working webcam
Setup
Clone the repository:
git clone https://github.com/jiyajiyabhola888-blip/AI-Virtual-Mouse.git
Open the project directory:
cd AI-Virtual-Mouse
Create a virtual environment:
python -m venv venv
Activate it:
venv\Scripts\activate
Install dependencies:
pip install -r requirements.txt
▶️ Running the Application
Run from the project root:
python -m src.main
Or use the Windows launcher:
run.bat
🧪 Testing
The project includes an automated test suite for checking the core functionality.
Run:
python test_system.py
The test suite checks components such as:
Letter recognition
Trajectory processing
Template availability
System components
Recognition functionality
🔮 Future Scope
The project can be further extended with:
Full A–Z Air-Writing
More gesture-based computer controls
Custom gesture mapping
Multi-hand interaction
Voice + gesture control
Improved letter recognition
Personalized recognition models
Cross-platform support
Accessibility-focused interaction modes
🎓 Learning & Applications
This project demonstrates practical implementation of:
Computer Vision → Hand Tracking → Gesture Recognition → Human-Computer Interaction → Desktop Automation
It can serve as a foundation for developing more advanced AI-powered, touch-free interfaces.
👩‍💻 Author
Jiya Bhola
B.Tech CSE | AI/ML
GitHub:
https://github.com/jiyajiyabhola888-blip⁠
