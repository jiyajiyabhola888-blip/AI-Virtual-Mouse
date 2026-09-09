"""
Main application entry point for Virtual AI Mouse & Keyboard.
Orchestrates camera acquisition, hand tracking, gesture prioritization,
air-writing, dual-mode letter recognition, app launching, and HUD visualization.
"""
import datetime
import sys
import threading
import time
from pathlib import Path
import cv2
import numpy as np
import pyautogui

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.hand_tracker import HandTracker
from src.mouse_controller import MouseController
from src.air_writer import AirWriter
from src.recognizer import LetterRecognizer
from src.app_launcher import AppLauncher
from src.camera_preview import HUDRenderer


class ThreadedCamera:
    """
    High-performance threaded camera frame grabber.
    Continuously pulls frames from the hardware camera buffer in a dedicated background thread
    so cap.read() returns the freshest frame with 0ms latency.
    """

    def __init__(
        self,
        src: int = config.CAMERA_ID,
        width: int = config.FRAME_WIDTH,
        height: int = config.FRAME_HEIGHT,
        fps: int = config.FPS_TARGET,
    ):
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened() and src == 0:
            self.cap = cv2.VideoCapture(1)

        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            try:
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass
            self.status, self.frame = self.cap.read()
        else:
            self.status = False
            self.frame = None

        self.lock = threading.Lock()
        self.stopped = False
        self.thread = threading.Thread(target=self._update, daemon=True)
        if self.cap.isOpened():
            self.thread.start()

    def _update(self):
        while not self.stopped:
            if self.cap and self.cap.isOpened():
                grabbed, frame = self.cap.read()
                if grabbed and frame is not None:
                    with self.lock:
                        self.frame = frame
                        self.status = grabbed
                else:
                    time.sleep(0.005)
            else:
                time.sleep(0.02)

    def read(self):
        with self.lock:
            if self.frame is not None:
                return self.status, self.frame.copy()
            return False, None

    def isOpened(self):
        return self.cap and self.cap.isOpened()

    def release(self):
        self.stopped = True
        if self.thread.is_alive():
            self.thread.join(timeout=0.3)
        if self.cap and self.cap.isOpened():
            self.cap.release()


def print_startup_banner():
    """Prints standard clean startup log to console."""
    print("============================================================")
    print("        VIRTUAL AI MOUSE & KEYBOARD")
    print("============================================================")
    print("")


def main():
    print_startup_banner()

    # 1. Initialize Threaded Zero-Latency Camera
    cap = ThreadedCamera(
        src=config.CAMERA_ID,
        width=config.FRAME_WIDTH,
        height=config.FRAME_HEIGHT,
        fps=config.FPS_TARGET,
    )
    if cap.isOpened():
        print("[INFO] High-performance zero-latency camera initialized")
    else:
        print("[ERROR] No working webcam detected. Running in camera retry / simulation mode.")

    # 2. Initialize Subsystems
    try:
        tracker = HandTracker()
        print("[INFO] Hand tracker initialized")
    except Exception as e:
        print(f"[ERROR] Hand tracker initialization failed: {e}")
        return

    try:
        mouse = MouseController()
        print("[INFO] Mouse controller initialized")
    except Exception as e:
        print(f"[ERROR] Mouse controller initialization failed: {e}")
        return

    try:
        air_writer = AirWriter()
        print("[INFO] Air writer initialized")
    except Exception as e:
        print(f"[ERROR] Air writer initialization failed: {e}")
        return

    try:
        recognizer = LetterRecognizer()
        print("[INFO] Letter recognizer initialized")
    except Exception as e:
        print(f"[ERROR] Letter recognizer initialization failed: {e}")
        return

    try:
        launcher = AppLauncher()
        print("[INFO] App launcher initialized")
    except Exception as e:
        print(f"[ERROR] App launcher initialization failed: {e}")
        return

    try:
        hud = HUDRenderer()
        print("[INFO] Camera preview initialized")
    except Exception as e:
        print(f"[ERROR] Camera preview initialization failed: {e}")
        return

    print("[INFO] System running\n")

    # State variables
    prev_time = time.time()
    last_screenshot_time = 0.0
    last_recognition_time = 0.0
    last_recognized_letter: str | None = None
    last_recognized_score: float | None = None
    last_action_text = "Idle"
    current_mode = "IDLE"

    # Main Application Loop
    while True:
        loop_start = time.time()

        if cap and cap.isOpened():
            success, frame = cap.read()
            if not success or frame is None or frame.size == 0:
                # Handle temporary camera read glitch
                time.sleep(0.03)
                continue
        else:
            # Fallback blank frame if camera hardware disconnected
            frame = np.zeros((config.FRAME_HEIGHT, config.FRAME_WIDTH, 3), dtype=np.uint8)
            cv2.putText(
                frame,
                "Webcam not connected. Reconnecting...",
                (100, config.FRAME_HEIGHT // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

        # 1. Preprocessing (Horizontal Mirroring)
        if config.FLIP_HORIZONTAL:
            frame = cv2.flip(frame, 1)

        # 2. Hand Tracking
        hands, annotated_frame = tracker.find_hands(frame, draw=True)
        hand = hands[0] if hands else None
        fingers = tracker.get_fingers_up(hand) if hand else [0, 0, 0, 0, 0]

        now = time.time()
        is_writing = False

        # --------------------------------------------------
        # GESTURE PRIORITY ENGINE
        # --------------------------------------------------
        if hand:
            # Check for Air-Writing Gesture [0, 1, 1, 0, 0] (Priority 1)
            is_writing_now, has_drawing_finished = air_writer.update(hand, fingers)

            if is_writing_now:
                # PRIORITY 1: AIR-WRITING ACTIVE
                current_mode = "AIR WRITING"
                last_action_text = "Drawing Stroke"
                is_writing = True
                # Mouse actions completely disabled during writing

            elif has_drawing_finished:
                # WRITING COMPLETED -> Trigger One-Shot Recognition & App Launch
                if (now - last_recognition_time) > config.RECOGNITION_COOLDOWN:
                    raw_points = air_writer.get_points()
                    if len(raw_points) >= config.MIN_DRAWING_POINTS:
                        best_letter, best_score, _ = recognizer.recognize(raw_points)
                        last_recognized_letter = best_letter
                        last_recognized_score = best_score
                        last_recognition_time = now

                        # Launch mapped application
                        success, launch_msg = launcher.launch(best_letter)
                        hud.show_toast(launch_msg, config.COLOR_ACCENT_GREEN, duration=3.5)

                    air_writer.clear()
                current_mode = "MOUSE"

            # PRIORITY 2: SCREENSHOT GESTURE [1, 1, 1, 1, 1] (Open Hand)
            elif sum(fingers) == 5:
                current_mode = "SCREENSHOT"
                last_action_text = "Open Hand"
                if (now - last_screenshot_time) > config.SCREENSHOT_COOLDOWN:
                    try:
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"shot_{timestamp}.png"
                        save_path = config.SCREENSHOTS_DIR / filename
                        screenshot = pyautogui.screenshot()
                        screenshot.save(str(save_path))
                        last_screenshot_time = now
                        log_msg = f"[SCREENSHOT] Saved {filename}"
                        print(log_msg)
                        hud.show_toast(log_msg, config.COLOR_ACCENT_PURPLE, duration=3.0)
                    except Exception as e:
                        print(f"[ERROR] Failed to save screenshot: {e}")

            # PRIORITY 3 & 4: MOUSE GESTURES & CURSOR MOVEMENT
            else:
                current_mode = "MOUSE"
                last_action_text = mouse.process_mouse_gestures(
                    hand=hand,
                    fingers=fingers,
                    tracker=tracker,
                    frame=annotated_frame,
                )

        else:
            # No hand detected
            current_mode = "IDLE"
            last_action_text = "No Hand"
            # If user drew something and removed hand, finalize drawing
            _, has_drawing_finished = air_writer.update(None, [0, 0, 0, 0, 0])
            if has_drawing_finished and air_writer.has_points():
                if (now - last_recognition_time) > config.RECOGNITION_COOLDOWN:
                    raw_points = air_writer.get_points()
                    if len(raw_points) >= config.MIN_DRAWING_POINTS:
                        best_letter, best_score, _ = recognizer.recognize(raw_points)
                        last_recognized_letter = best_letter
                        last_recognized_score = best_score
                        last_recognition_time = now

                        success, launch_msg = launcher.launch(best_letter)
                        hud.show_toast(launch_msg, config.COLOR_ACCENT_GREEN, duration=3.5)

                    air_writer.clear()

        # 3. Draw Air Writing strokes onto frame
        annotated_frame = air_writer.draw_on_frame(annotated_frame, show_pointer=is_writing)

        # 4. Compute FPS
        curr_time = time.time()
        fps = 1.0 / max(curr_time - prev_time, 1e-5)
        prev_time = curr_time

        # 5. Render HUD Overlay
        output_frame = hud.render_hud(
            frame=annotated_frame,
            mode_name=current_mode,
            fingers=fingers,
            last_letter=last_recognized_letter,
            last_score=last_recognized_score,
            last_action=last_action_text,
            fps=fps,
            is_writing=is_writing,
            cursor_pos=(int(mouse.curr_x), int(mouse.curr_y)),
        )

        # 6. Display Video Frame
        cv2.imshow(config.WINDOW_TITLE, output_frame)

        # 7. Keyboard Shortcuts Handling
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q"), 27):  # 'Q' or ESC to quit
            print("[INFO] Clean exit requested by user")
            break
        elif key in (ord("c"), ord("C")):    # 'C' to clear air-writing canvas
            air_writer.clear()
            hud.show_toast("Canvas cleared", config.COLOR_ACCENT_CYAN, duration=1.5)
            print("[INFO] Air-writing canvas cleared")
        elif key in (ord("s"), ord("S")):    # 'S' manual screenshot
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"shot_{timestamp}.png"
                save_path = config.SCREENSHOTS_DIR / filename
                screenshot = pyautogui.screenshot()
                screenshot.save(str(save_path))
                log_msg = f"[SCREENSHOT] Saved {filename}"
                print(log_msg)
                hud.show_toast(log_msg, config.COLOR_ACCENT_PURPLE, duration=3.0)
            except Exception as e:
                print(f"[ERROR] Failed to save screenshot: {e}")

    # Cleanup and release
    mouse.release_all()
    if cap and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Application shut down cleanly")


if __name__ == "__main__":
    main()
