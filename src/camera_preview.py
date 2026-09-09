"""
Camera Preview and HUD Renderer module.
Draws a polished, modern HUD overlay with mode badges, finger telemetry,
gesture cheatsheet, active mouse mapping boundaries, toast notifications,
cursor position telemetry, and recognition cards.
"""
import time
import cv2
import numpy as np
from src import config


class HUDRenderer:
    """
    Renders high-quality graphical HUD elements on the OpenCV preview frame.
    """

    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.toast_message = ""
        self.toast_start_time = 0.0
        self.toast_duration = 3.0
        self.toast_color = config.COLOR_ACCENT_GREEN

    def show_toast(self, message: str, color: tuple[int, int, int] = config.COLOR_ACCENT_GREEN, duration: float = 3.0):
        """Displays a floating toast alert on the HUD."""
        self.toast_message = message
        self.toast_color = color
        self.toast_start_time = time.time()
        self.toast_duration = duration

    def _draw_rounded_rect(
        self,
        img: np.ndarray,
        pt1: tuple[int, int],
        pt2: tuple[int, int],
        color: tuple[int, int, int],
        thickness: int = 1,
        radius: int = 10,
    ):
        """Draws a rounded rectangle using OpenCV primitives."""
        x1, y1 = pt1
        x2, y2 = pt2
        r = radius

        # Corners
        cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness, lineType=cv2.LINE_AA)
        cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness, lineType=cv2.LINE_AA)
        cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness, lineType=cv2.LINE_AA)
        cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness, lineType=cv2.LINE_AA)

        # Edges
        cv2.line(img, (x1 + r, y1), (x2 - r, y1), color, thickness, lineType=cv2.LINE_AA)
        cv2.line(img, (x1 + r, y2), (x2 - r, y2), color, thickness, lineType=cv2.LINE_AA)
        cv2.line(img, (x1, y1 + r), (x1, y2 - r), color, thickness, lineType=cv2.LINE_AA)
        cv2.line(img, (x2, y1 + r), (x2, y2 - r), color, thickness, lineType=cv2.LINE_AA)

    def _draw_card_background(
        self,
        img: np.ndarray,
        pt1: tuple[int, int],
        pt2: tuple[int, int],
        bg_color: tuple[int, int, int] = config.COLOR_CARD_BG,
        alpha: float = 0.75,
        border_color: tuple[int, int, int] = config.COLOR_BORDER,
        radius: int = 8,
    ):
        """Draws a semi-transparent glassmorphic card background using ultra-fast in-place ROI slice blending."""
        h_frame, w_frame = img.shape[:2]
        x1 = max(0, min(w_frame - 1, int(pt1[0])))
        y1 = max(0, min(h_frame - 1, int(pt1[1])))
        x2 = max(0, min(w_frame, int(pt2[0])))
        y2 = max(0, min(h_frame, int(pt2[1])))

        if x2 > x1 and y2 > y1:
            roi = img[y1:y2, x1:x2]
            color_rect = np.full_like(roi, bg_color, dtype=np.uint8)
            cv2.addWeighted(color_rect, alpha, roi, 1.0 - alpha, 0, roi)
            self._draw_rounded_rect(img, (x1, y1), (x2, y2), border_color, thickness=1, radius=radius)

    def render_hud(
        self,
        frame: np.ndarray,
        mode_name: str,
        fingers: list[int],
        last_letter: str | None,
        last_score: float | None,
        last_action: str,
        fps: float,
        is_writing: bool = False,
        cursor_pos: tuple[int, int] | None = None,
    ) -> np.ndarray:
        """
        Renders all HUD panels, badges, cheatsheet, and metrics onto the frame.
        """
        h, w, _ = frame.shape

        # 1. DRAW MOUSE INTERACTION ROI BOUNDARY (Subtle boundary box)
        rx, ry = config.FRAME_REDUCTION_X, config.FRAME_REDUCTION_Y
        roi_color = (120, 100, 80) if not is_writing else (80, 80, 80)
        self._draw_rounded_rect(
            frame,
            (rx, ry),
            (w - rx, h - ry),
            roi_color,
            thickness=1,
            radius=12,
        )

        # 2. TOP HEADER BAR
        self._draw_card_background(frame, (16, 14), (w - 16, 68), alpha=0.82)

        # Title
        cv2.putText(
            frame,
            "VIRTUAL AI MOUSE & KEYBOARD",
            (32, 48),
            self.font,
            0.72,
            config.COLOR_TEXT_PRIMARY,
            2,
            lineType=cv2.LINE_AA,
        )

        # Mode Badge
        if mode_name == "AIR WRITING":
            badge_color = config.COLOR_ACCENT_ORANGE
        elif mode_name == "SCREENSHOT":
            badge_color = config.COLOR_ACCENT_PURPLE
        elif mode_name == "MOUSE":
            badge_color = config.COLOR_ACCENT_GREEN
        else:
            badge_color = config.COLOR_TEXT_MUTED

        badge_x = 510
        self._draw_card_background(frame, (badge_x, 22), (badge_x + 195, 58), bg_color=badge_color, alpha=0.85)
        cv2.putText(
            frame,
            f"MODE: {mode_name}",
            (badge_x + 14, 46),
            self.font,
            0.55,
            (0, 0, 0),
            2,
            lineType=cv2.LINE_AA,
        )

        # Action / State indicator
        cv2.putText(
            frame,
            f"Action: {last_action}",
            (725, 46),
            self.font,
            0.52,
            config.COLOR_ACCENT_CYAN,
            1,
            lineType=cv2.LINE_AA,
        )

        # FPS indicator
        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (w - 110, 46),
            self.font,
            0.52,
            config.COLOR_ACCENT_GREEN,
            1,
            lineType=cv2.LINE_AA,
        )

        # 3. FINGERS TELEMETRY CARD (Top Left under header)
        self._draw_card_background(frame, (16, 80), (280, 155), alpha=0.80)
        cv2.putText(
            frame,
            "DETECTED FINGERS",
            (28, 102),
            self.font,
            0.42,
            config.COLOR_TEXT_MUTED,
            1,
            lineType=cv2.LINE_AA,
        )

        finger_labels = ["T", "I", "M", "R", "P"]
        start_fx = 28
        for i, (lbl, val) in enumerate(zip(finger_labels, fingers)):
            fx = start_fx + (i * 48)
            f_color = config.COLOR_ACCENT_GREEN if val == 1 else (90, 90, 100)
            cv2.circle(frame, (fx + 12, 128), 12, f_color, cv2.FILLED, lineType=cv2.LINE_AA)
            cv2.putText(
                frame,
                lbl,
                (fx + 7, 133),
                self.font,
                0.40,
                (0, 0, 0) if val == 1 else (180, 180, 180),
                1,
                lineType=cv2.LINE_AA,
            )

        # Cursor coordinates display
        if cursor_pos:
            cv2.putText(
                frame,
                f"Cursor: {cursor_pos[0]}, {cursor_pos[1]}",
                (28, 150),
                self.font,
                0.36,
                config.COLOR_ACCENT_CYAN,
                1,
                lineType=cv2.LINE_AA,
            )

        # 4. RECOGNITION CARD (Top Right under header)
        self._draw_card_background(frame, (w - 296, 80), (w - 16, 195), alpha=0.82)
        cv2.putText(
            frame,
            "LAST RECOGNITION",
            (w - 280, 104),
            self.font,
            0.44,
            config.COLOR_TEXT_MUTED,
            1,
            lineType=cv2.LINE_AA,
        )

        disp_letter = last_letter if last_letter else "--"
        disp_score = f"{last_score:.2f}" if last_score is not None else "--"
        mapped_app = config.APP_MAPPINGS.get(disp_letter, {}).get("name", "") if last_letter else ""

        cv2.putText(
            frame,
            f"Letter: {disp_letter}",
            (w - 280, 136),
            self.font,
            0.75,
            config.COLOR_ACCENT_ORANGE,
            2,
            lineType=cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            f"Score:  {disp_score}",
            (w - 280, 162),
            self.font,
            0.55,
            config.COLOR_ACCENT_CYAN,
            1,
            lineType=cv2.LINE_AA,
        )
        if mapped_app:
            cv2.putText(
                frame,
                f"App: {mapped_app}",
                (w - 280, 184),
                self.font,
                0.42,
                config.COLOR_TEXT_PRIMARY,
                1,
                lineType=cv2.LINE_AA,
            )

        # 5. AIR-WRITING INSTRUCTION BANNER (Bottom Center when drawing or ready)
        if is_writing or mode_name == "AIR WRITING":
            prompt_w = 460
            px1 = (w - prompt_w) // 2
            px2 = px1 + prompt_w
            self._draw_card_background(frame, (px1, h - 85), (px2, h - 35), bg_color=(20, 60, 90), alpha=0.85)
            cv2.putText(
                frame,
                "Write one letter clearly in the air [W, Y, G, I, C, N]",
                (px1 + 18, h - 55),
                self.font,
                0.48,
                (0, 240, 255),
                1,
                lineType=cv2.LINE_AA,
            )

        # 6. GESTURE CHEATSHEET PANEL (Bottom Left)
        self._draw_card_background(frame, (16, h - 235), (280, h - 16), alpha=0.82)
        cv2.putText(
            frame,
            "GESTURE CONTROLS",
            (28, h - 212),
            self.font,
            0.44,
            config.COLOR_TEXT_MUTED,
            1,
            lineType=cv2.LINE_AA,
        )

        gestures = [
            ("Index", "Move Cursor"),
            ("Thumb+Index", "Left Click"),
            ("Thumb+Middle", "Right Click"),
            ("Thumb+Ring", "Double Click"),
            ("Thumb+Pinky", "Drag / Drop"),
            ("Index+Middle", "Air-Write [W,Y,G,I,C,N]"),
            ("Open Hand", "Screenshot"),
        ]

        gy = h - 190
        for trigger, desc in gestures:
            cv2.putText(
                frame,
                f"{trigger:<12} = {desc}",
                (28, gy),
                self.font,
                0.36,
                config.COLOR_TEXT_PRIMARY,
                1,
                lineType=cv2.LINE_AA,
            )
            gy += 18

        # Shortcuts footer
        cv2.putText(
            frame,
            "[C] Clear Drawing    [Q] Quit",
            (28, h - 26),
            self.font,
            0.38,
            config.COLOR_ACCENT_CYAN,
            1,
            lineType=cv2.LINE_AA,
        )

        # 7. TOAST NOTIFICATION
        if self.toast_message and (time.time() - self.toast_start_time) < self.toast_duration:
            toast_w = 480
            tx1 = (w - toast_w) // 2
            tx2 = tx1 + toast_w
            self._draw_card_background(frame, (tx1, 80), (tx2, 126), bg_color=config.COLOR_BG_DARK, alpha=0.90)
            cv2.putText(
                frame,
                self.toast_message,
                (tx1 + 20, 110),
                self.font,
                0.52,
                self.toast_color,
                1,
                lineType=cv2.LINE_AA,
            )

        return frame
