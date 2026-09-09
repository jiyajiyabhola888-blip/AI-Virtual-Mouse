🖱️ Virtual AI Mouse & Air-Writing Keyboard
A real-time AI-powered Human-Computer Interaction system that enables users to control a computer using hand gestures and air-writing through a webcam.
📌 Overview
Virtual AI Mouse & Air-Writing Keyboard is a Computer Vision and Artificial Intelligence based desktop application that transforms hand movements into real-time computer commands without requiring a traditional mouse or keyboard.
Using a webcam, the system detects and tracks the user's hand through MediaPipe's 21 hand landmarks and interprets various finger gestures to perform actions such as:
Cursor Movement
Left Click
Right Click
Double Click
Drag & Drop
Screenshot Capture
In addition to gesture-based control, the project introduces an Air-Writing Keyboard, where users can write supported letters in the air using their index finger. The system analyzes the finger trajectory, recognizes the written character, and automatically launches the mapped application or website.
The entire solution operates locally on the user's machine, providing a touch-free and intuitive Human-Computer Interaction (HCI) experience.
🎯 Problem Statement
Traditional computer interaction relies heavily on physical devices such as a mouse and keyboard. These devices can be limiting in situations where touch-free interaction, accessibility, or hands-free control is required.
This project addresses these challenges by providing:
✅ Touch-free computer control
✅ AI-based gesture interaction
✅ Air-writing based application launching
✅ Accessibility-focused user experience
✅ Human-Computer Interaction research platform
✅ Smart desktop automation using Computer Vision
⚙️ Working Principle
Virtual Mouse Workflow
Webcam
   ↓
Hand Detection
   ↓
21 Landmark Tracking
   ↓
Gesture Recognition
   ↓
Mouse Action Execution
Air-Writing Workflow
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
Mapped Application Launch
🧠 Core Technologies
The system combines multiple AI and Computer Vision techniques:
MediaPipe Hand Landmark Detection
OpenCV Image Processing
Gesture Recognition
Trajectory Analysis
Template Matching
Desktop Automation with PyAutoGUI
Using 21 hand landmarks, the system identifies:
Finger positions
Raised fingers
Finger touch events
Hand movement patterns
Writing trajectories
Gesture classifications
These features are converted into corresponding computer actions in real time.
✨ Key Features
🖱️ Gesture-Based Virtual Mouse
Gesture
Action
☝️ Index Finger
Cursor Movement
🤏 Thumb + Index
Left Click
🤏 Thumb + Middle
Right Click
🤏 Thumb + Ring
Double Click
🤏 Thumb + Pinky
Drag & Drop
🖐️ Open Hand
Screenshot Capture
✍️ Air-Writing Keyboard
Activate Air-Writing mode by raising:
Index Finger + Middle Finger
The system tracks the fingertip trajectory and recognizes the written character.
🔤 Supported Air-Written Commands
Letter
Action
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
Notepad
Example:
Draw "W"
      ↓
Recognized
      ↓
WhatsApp Web Opens
🧩 Hybrid Letter Recognition
The recognition engine combines:
Trajectory Analysis
Template Matching
This dual-recognition approach improves accuracy and robustness compared to single-method systems.
📸 Gesture-Based Screenshot
Raise all five fingers:
🖐️ → Screenshot Captured
Screenshots are automatically saved with timestamp-based filenames.
🏗️ System Architecture
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
             │ Virtual      │    │ Air-Writing │
             │ Mouse        │    │ Recognition │
             └──────┬──────┘    └──────┬──────┘
                    ↓                   ↓
             Mouse Actions       Letter Detection
                                        ↓
                                 Application Launcher
🛠️ Technology Stack
Python
OpenCV
MediaPipe
cvzone
PyAutoGUI
NumPy
Git & GitHub
🚀 Future Scope
Full A–Z Air-Writing Support
Custom Gesture Mapping
Multi-Hand Interaction
Voice + Gesture Integration
Personalized AI Recognition Models
Cross-Platform Compatibility
Advanced Accessibility Features
🎓 Applications
Human-Computer Interaction (HCI)
Accessibility Systems
Smart Classrooms
Touch-Free Interfaces
AI-Based Desktop Automation
Computer Vision Research
