"""
Virtual Mouse Controller module.
Uses Windows Win32 API (ctypes) for zero-latency cursor movement and clicking,
with PyAutoGUI fallback. Features adaptive hand scale normalization,
EMA anti-jitter smoothing, and real-time visual gesture feedback.
"""
import ctypes
import math
import time
import cv2
import numpy as np
import pyautogui
from src import config

# Disable PyAutoGUI failsafe to prevent edge-of-screen crashes
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0

# Windows Mouse Event Flags (Win32 API)
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000


class MouseController:
    """
    Translates hand landmarks into smooth mouse cursor movement and click/drag gestures.
    """

    def __init__(self):
        self.screen_w = config.SCREEN_WIDTH
        self.screen_h = config.SCREEN_HEIGHT

        # Smoothed cursor position
        self.prev_x = float(self.screen_w // 2)
        self.prev_y = float(self.screen_h // 2)
        self.curr_x = self.prev_x
        self.curr_y = self.prev_y

        # State tracking
        self.is_dragging = False
        self.last_action_name = "Idle"

        # Cooldown timestamps
        self.last_left_click_time = 0.0
        self.last_right_click_time = 0.0
        self.last_double_click_time = 0.0

    def _win32_set_cursor(self, x: int, y: int):
        """Sets cursor position using Win32 API (0ms latency)."""
        try:
            ctypes.windll.user32.SetCursorPos(int(x), int(y))
        except Exception:
            try:
                pyautogui.moveTo(int(x), int(y))
            except Exception:
                pass

    def _win32_mouse_event(self, flags: int):
        """Dispatches mouse click events using Win32 API."""
        try:
            ctypes.windll.user32.mouse_event(flags, 0, 0, 0, 0)
        except Exception:
            pass

    def left_click(self):
        """Executes a single left mouse click with zero latency."""
        try:
            self._win32_mouse_event(MOUSEEVENTF_LEFTDOWN)
            self._win32_mouse_event(MOUSEEVENTF_LEFTUP)
        except Exception:
            try:
                pyautogui.click()
            except Exception:
                pass

    def right_click(self):
        """Executes a single right mouse click with zero latency."""
        try:
            self._win32_mouse_event(MOUSEEVENTF_RIGHTDOWN)
            self._win32_mouse_event(MOUSEEVENTF_RIGHTUP)
        except Exception:
            try:
                pyautogui.rightClick()
            except Exception:
                pass

    def double_click(self):
        """Executes a double left click with zero latency."""
        try:
            self._win32_mouse_event(MOUSEEVENTF_LEFTDOWN)
            self._win32_mouse_event(MOUSEEVENTF_LEFTUP)
            self._win32_mouse_event(MOUSEEVENTF_LEFTDOWN)
            self._win32_mouse_event(MOUSEEVENTF_LEFTUP)
        except Exception:
            try:
                pyautogui.doubleClick()
            except Exception:
                pass

    def move_cursor(self, finger_x: int, finger_y: int) -> tuple[int, int]:
        """
        Maps fingertip coordinates within the camera ROI to the display screen,
        applying velocity-adaptive smoothing to eliminate jitter while providing
        instant zero-latency movement for fast motions.
        """
        # Interpolate from camera reduction box to full screen coordinates
        target_x = np.interp(
            finger_x,
            (config.FRAME_REDUCTION_X, config.FRAME_WIDTH - config.FRAME_REDUCTION_X),
            (0, self.screen_w),
        )
        target_y = np.interp(
            finger_y,
            (config.FRAME_REDUCTION_Y, config.FRAME_HEIGHT - config.FRAME_REDUCTION_Y),
            (0, self.screen_h),
        )

        # Clamp within screen bounds
        target_x = max(0.0, min(float(self.screen_w - 1), float(target_x)))
        target_y = max(0.0, min(float(self.screen_h - 1), float(target_y)))

        # Calculate distance / velocity
        dx = target_x - self.prev_x
        dy = target_y - self.prev_y
        dist = math.hypot(dx, dy)

        # Deadzone filtering: Ignore micro-tremors when hand is stationary
        deadzone = getattr(config, "CURSOR_DEADZONE", 1.5)
        if dist < deadzone:
            self._win32_set_cursor(int(self.curr_x), int(self.curr_y))
            return int(self.curr_x), int(self.curr_y)

        # Dynamic Velocity-Adaptive Alpha:
        # Smooth transition between ALPHA_MIN (fine precision) and ALPHA_MAX (instant fast follow)
        alpha_min = getattr(config, "CURSOR_EMA_ALPHA_MIN", 0.28)
        alpha_max = getattr(config, "CURSOR_EMA_ALPHA_MAX", 0.92)
        speed_thresh = getattr(config, "CURSOR_SPEED_THRESHOLD", 45.0)

        # Speed factor with smooth power curve for natural buttery feel
        speed_factor = min(1.0, dist / max(speed_thresh, 1.0))
        alpha = alpha_min + (alpha_max - alpha_min) * (speed_factor ** 1.4)

        self.curr_x = self.prev_x + alpha * dx
        self.curr_y = self.prev_y + alpha * dy

        self.prev_x = self.curr_x
        self.prev_y = self.curr_y

        # Move system cursor
        self._win32_set_cursor(int(self.curr_x), int(self.curr_y))
        return int(self.curr_x), int(self.curr_y)

    def process_mouse_gestures(
        self,
        hand: dict,
        fingers: list[int],
        tracker,
        frame: np.ndarray | None = None,
    ) -> str:
        """
        Processes mouse gestures based on finger states and adaptive pinch ratios.
        Gesture Priority:
          1. Thumb + Pinky  -> Drag / Drop
          2. Thumb + Ring   -> Double Click
          3. Thumb + Middle -> Right Click
          4. Thumb + Index  -> Left Click
          5. Index only     -> Move Cursor

        Returns:
            action_name: name of current action performed
        """
        lm_list = hand.get("lmList", [])
        if len(lm_list) < 21:
            return "No Landmarks"

        now = time.time()
        p_thumb = lm_list[4][:2]
        p_index = lm_list[8][:2]
        p_middle = lm_list[12][:2]
        p_ring = lm_list[16][:2]
        p_pinky = lm_list[20][:2]

        hand_scale = tracker.get_hand_scale(lm_list)

        # Calculate distances & adaptive pinch ratios
        dist_thumb_index = math.hypot(p_thumb[0] - p_index[0], p_thumb[1] - p_index[1])
        dist_thumb_middle = math.hypot(p_thumb[0] - p_middle[0], p_thumb[1] - p_middle[1])
        dist_thumb_ring = math.hypot(p_thumb[0] - p_ring[0], p_thumb[1] - p_ring[1])
        dist_thumb_pinky = math.hypot(p_thumb[0] - p_pinky[0], p_thumb[1] - p_pinky[1])

        ratio_thumb_index = dist_thumb_index / hand_scale
        ratio_thumb_middle = dist_thumb_middle / hand_scale
        ratio_thumb_ring = dist_thumb_ring / hand_scale
        ratio_thumb_pinky = dist_thumb_pinky / hand_scale

        # Pinch detection thresholds (adaptive + pixel bounds)
        is_pinching_index = (ratio_thumb_index < config.PINCH_RATIO_THRESHOLD) or (dist_thumb_index < config.CLICK_DISTANCE_THRESHOLD)
        is_pinching_middle = (ratio_thumb_middle < config.PINCH_RATIO_THRESHOLD) or (dist_thumb_middle < config.CLICK_DISTANCE_THRESHOLD)
        is_pinching_ring = (ratio_thumb_ring < config.PINCH_RATIO_THRESHOLD) or (dist_thumb_ring < config.CLICK_DISTANCE_THRESHOLD)
        is_pinching_pinky = (ratio_thumb_pinky < config.DRAG_PINCH_RATIO_THRESHOLD) or (dist_thumb_pinky < config.DRAG_DISTANCE_THRESHOLD)

        # Always update cursor position to follow Index fingertip when hand is active
        self.move_cursor(p_index[0], p_index[1])

        # 1. DRAG GESTURE (Thumb + Pinky pinch)
        if is_pinching_pinky:
            if not self.is_dragging:
                self._win32_mouse_event(MOUSEEVENTF_LEFTDOWN)
                self.is_dragging = True
                print("[MOUSE] Drag started")

            if frame is not None:
                cv2.line(frame, tuple(p_thumb), tuple(p_pinky), (255, 0, 255), 3, lineType=cv2.LINE_AA)
                cv2.circle(frame, tuple(p_pinky), 12, (255, 0, 255), cv2.FILLED, lineType=cv2.LINE_AA)

            action = "Dragging"
            self.last_action_name = action
            return action

        elif self.is_dragging:
            # Drag released
            self._win32_mouse_event(MOUSEEVENTF_LEFTUP)
            self.is_dragging = False
            print("[MOUSE] Drag released")

        # 2. DOUBLE CLICK (Thumb + Ring pinch)
        if is_pinching_ring:
            if (now - self.last_double_click_time) > config.DOUBLE_CLICK_COOLDOWN:
                self.double_click()
                self.last_double_click_time = now
                print("[MOUSE] Double Click")

            if frame is not None:
                cv2.line(frame, tuple(p_thumb), tuple(p_ring), (255, 200, 0), 3, lineType=cv2.LINE_AA)
                cv2.circle(frame, tuple(p_ring), 12, (255, 200, 0), cv2.FILLED, lineType=cv2.LINE_AA)

            action = "Double Click"
            self.last_action_name = action
            return action

        # 3. RIGHT CLICK (Thumb + Middle pinch)
        if is_pinching_middle:
            if (now - self.last_right_click_time) > config.CLICK_COOLDOWN:
                self.right_click()
                self.last_right_click_time = now
                print("[MOUSE] Right Click")

            if frame is not None:
                cv2.line(frame, tuple(p_thumb), tuple(p_middle), (0, 255, 255), 3, lineType=cv2.LINE_AA)
                cv2.circle(frame, tuple(p_middle), 12, (0, 255, 255), cv2.FILLED, lineType=cv2.LINE_AA)

            action = "Right Click"
            self.last_action_name = action
            return action

        # 4. LEFT CLICK (Thumb + Index pinch)
        if is_pinching_index:
            if (now - self.last_left_click_time) > config.CLICK_COOLDOWN:
                self.left_click()
                self.last_left_click_time = now
                print("[MOUSE] Left Click")

            if frame is not None:
                cv2.line(frame, tuple(p_thumb), tuple(p_index), (0, 255, 0), 3, lineType=cv2.LINE_AA)
                cv2.circle(frame, tuple(p_index), 14, (0, 255, 0), cv2.FILLED, lineType=cv2.LINE_AA)

            action = "Left Click"
            self.last_action_name = action
            return action

        # 5. CURSOR MOVEMENT (Index finger is up / standard tracking)
        if frame is not None:
            # Draw cursor pointer indicator on index tip
            cv2.circle(frame, tuple(p_index), 10, (255, 255, 0), 2, lineType=cv2.LINE_AA)
            cv2.circle(frame, tuple(p_index), 4, (0, 255, 255), cv2.FILLED, lineType=cv2.LINE_AA)

        action = "Move Cursor"
        self.last_action_name = action
        return action

    def release_all(self):
        """Releases any active mouse holds on exit."""
        if self.is_dragging:
            self._win32_mouse_event(MOUSEEVENTF_LEFTUP)
            self.is_dragging = False
