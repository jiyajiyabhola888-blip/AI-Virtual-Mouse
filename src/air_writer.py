"""
Air-Writing module.
Tracks the index fingertip when in writing gesture [0, 1, 1, 0, 0],
records the trajectory, renders smooth glowing strokes on screen,
and manages writing completion states.
"""
import math
import time
import cv2
import numpy as np
from src import config


class AirWriter:
    """
    Handles air-writing point collection, stroke rendering, and state management.
    """

    def __init__(self):
        self.points: list[tuple[int, int]] = []
        self.is_writing = False
        self.has_completed_drawing = False
        self.last_write_time = 0.0
        self.last_point: tuple[int, int] | None = None

        # Dedicated transparent canvas for smooth rendering
        self.canvas = np.zeros((config.FRAME_HEIGHT, config.FRAME_WIDTH, 3), dtype=np.uint8)

    def is_writing_gesture(self, fingers: list[int]) -> bool:
        """
        Determines if current finger configuration matches the air-writing gesture.
        Pattern: Index and Middle UP, Ring and Pinky DOWN.
        """
        if not fingers or len(fingers) < 5:
            return False
        # Index & Middle up, Ring & Pinky down (Thumb can be 0 or 1)
        return bool(fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0)

    def add_point(self, x: int, y: int):
        """
        Adds a new point to the trajectory if it is valid and exceeds jitter threshold.
        """
        curr_pt = (int(x), int(y))
        now = time.time()

        if not self.points:
            self.points.append(curr_pt)
            self.last_point = curr_pt
            self.last_write_time = now
            return

        # Check Euclidean distance to last point to eliminate jitter and filter outliers
        prev_x, prev_y = self.points[-1]
        dist = math.hypot(curr_pt[0] - prev_x, curr_pt[1] - prev_y)

        # Minimum distance to avoid stacking identical points
        if dist >= 3.0:
            # Filter teleporting glitches from tracking loss
            if dist < 160.0 or len(self.points) < 3:
                self.points.append(curr_pt)
                self.last_point = curr_pt
                self.last_write_time = now

    def update(
        self,
        hand: dict | None,
        fingers: list[int],
    ) -> tuple[bool, bool]:
        """
        Updates writing state for the current frame.
        Returns:
            (is_writing_now, has_drawing_finished)
        """
        now = time.time()
        was_writing = self.is_writing

        if hand and self.is_writing_gesture(fingers):
            lm_list = hand.get("lmList", [])
            if len(lm_list) >= 9:
                idx_x, idx_y = lm_list[config.AIR_WRITING_LANDMARK][:2]
                self.add_point(idx_x, idx_y)
                self.is_writing = True
                self.has_completed_drawing = False
                return True, False

        # If not actively in writing gesture this frame:
        self.is_writing = False

        # Detect transition from writing -> finished drawing
        drawing_finished = False
        if was_writing and len(self.points) >= config.MIN_DRAWING_POINTS:
            drawing_finished = True
            self.has_completed_drawing = True
        elif not was_writing and len(self.points) >= config.MIN_DRAWING_POINTS:
            # Check for inactivity timeout if fingers lowered
            if (now - self.last_write_time) > config.WRITING_INACTIVITY_TIMEOUT and not self.has_completed_drawing:
                drawing_finished = True
                self.has_completed_drawing = True

        return False, drawing_finished

    def draw_on_frame(self, frame: np.ndarray, show_pointer: bool = True) -> np.ndarray:
        """
        Draws the recorded air-writing trajectory on top of the given video frame.
        Applies a multi-layered neon glow effect.
        """
        if frame is None or frame.size == 0:
            return frame

        pts_len = len(self.points)
        if pts_len > 1:
            # 1. Draw outer glow
            for i in range(1, pts_len):
                cv2.line(
                    frame,
                    self.points[i - 1],
                    self.points[i],
                    config.STROKE_GLOW_COLOR,
                    config.STROKE_GLOW_THICKNESS,
                    lineType=cv2.LINE_AA,
                )
            # 2. Draw core neon stroke
            for i in range(1, pts_len):
                cv2.line(
                    frame,
                    self.points[i - 1],
                    self.points[i],
                    config.STROKE_COLOR,
                    config.STROKE_THICKNESS,
                    lineType=cv2.LINE_AA,
                )

        # Draw writing tip cursor indicator if currently writing
        if self.is_writing and self.last_point:
            cv2.circle(
                frame,
                self.last_point,
                10,
                config.STROKE_COLOR,
                cv2.FILLED,
                lineType=cv2.LINE_AA,
            )
            cv2.circle(
                frame,
                self.last_point,
                16,
                (255, 255, 255),
                2,
                lineType=cv2.LINE_AA,
            )

        return frame

    def clear(self):
        """Resets all trajectory points and clears the canvas."""
        self.points.clear()
        self.is_writing = False
        self.has_completed_drawing = False
        self.last_point = None
        self.last_write_time = 0.0

    def get_points(self) -> list[tuple[int, int]]:
        """Returns a copy of the trajectory points."""
        return list(self.points)

    def has_points(self) -> bool:
        """Returns True if there is an active drawing with sufficient points."""
        return len(self.points) >= config.MIN_DRAWING_POINTS
