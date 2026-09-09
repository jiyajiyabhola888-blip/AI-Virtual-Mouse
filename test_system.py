"""
Automated unit and integration test suite for Virtual AI Mouse & Keyboard.
Verifies all modules, math algorithms, gesture prioritization, recognizer accuracy,
template loading, and safe app launching.
"""
import unittest
import numpy as np
from src import config
from src.recognizer import LetterRecognizer
from src.app_launcher import AppLauncher
from src.air_writer import AirWriter
from src.mouse_controller import MouseController
from src.camera_preview import HUDRenderer
from src.hand_tracker import HandTracker


class TestVirtualMouseKeyboard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.recognizer = LetterRecognizer()
        cls.launcher = AppLauncher()
        cls.writer = AirWriter()
        cls.mouse = MouseController()
        cls.hud = HUDRenderer()
        cls.tracker = HandTracker()

    def test_imports_and_config(self):
        """Test configuration constants and paths."""
        self.assertIn("W", config.SUPPORTED_LETTERS)
        self.assertIn("Y", config.SUPPORTED_LETTERS)
        self.assertIn("G", config.SUPPORTED_LETTERS)
        self.assertIn("I", config.SUPPORTED_LETTERS)
        self.assertIn("C", config.SUPPORTED_LETTERS)
        self.assertIn("N", config.SUPPORTED_LETTERS)
        self.assertEqual(len(config.SUPPORTED_LETTERS), 6)
        self.assertTrue(config.TEMPLATES_DIR.exists())
        self.assertTrue(config.SCREENSHOTS_DIR.exists())

    def test_template_existence(self):
        """Ensure all template PNG files exist."""
        for letter in config.SUPPORTED_LETTERS:
            tmpl_file = config.TEMPLATES_DIR / f"{letter}.png"
            self.assertTrue(tmpl_file.exists(), f"Missing template for {letter}")

    def test_app_launcher_mappings(self):
        """Ensure all letters have safe app targets."""
        for letter in config.SUPPORTED_LETTERS:
            self.assertIn(letter, self.launcher.mappings)
            app_info = self.launcher.mappings[letter]
            self.assertIn("name", app_info)
            self.assertIn("target", app_info)

    def test_air_writer_lifecycle(self):
        """Test point collection, smoothing, clearing in AirWriter."""
        writer = AirWriter()
        self.assertEqual(len(writer.get_points()), 0)
        self.assertFalse(writer.has_points())

        # Test writing gesture detection: [0, 1, 1, 0, 0]
        self.assertTrue(writer.is_writing_gesture([0, 1, 1, 0, 0]))
        self.assertTrue(writer.is_writing_gesture([1, 1, 1, 0, 0]))
        self.assertFalse(writer.is_writing_gesture([0, 1, 0, 0, 0]))
        self.assertFalse(writer.is_writing_gesture([1, 1, 1, 1, 1]))

        # Add points
        for i in range(25):
            writer.add_point(100 + i * 5, 200 + i * 3)

        self.assertTrue(writer.has_points())
        self.assertEqual(len(writer.get_points()), 25)

        writer.clear()
        self.assertEqual(len(writer.get_points()), 0)
        self.assertFalse(writer.has_points())

    def test_recognizer_synthetic_letters(self):
        """
        Verify that recognizer correctly scores synthetic strokes for W, Y, G, I, C, N
        and that trajectory scores are strictly positive (never 0.000).
        """
        # Define synthetic drawing paths in 1280x720 space
        synthetic_strokes = {
            "W": [
                (200, 200), (250, 450), (300, 300), (350, 450), (400, 200)
            ],
            "Y": [
                (200, 200), (300, 320), (300, 480), (300, 320), (400, 200)
            ],
            "G": [
                (400, 220), (280, 200), (200, 320), (280, 460), (400, 420), (400, 340), (310, 340)
            ],
            "I": [
                (300, 150), (300, 250), (300, 350), (300, 450), (300, 550)
            ],
            "C": [
                (400, 200), (280, 200), (200, 320), (280, 460), (400, 460)
            ],
            "N": [
                (200, 480), (200, 200), (380, 480), (380, 200)
            ],
        }

        print("\n--- Running Synthetic Letter Recognition Test ---")
        for expected_letter, stroke in synthetic_strokes.items():
            # Interpolate to create continuous polyline
            dense_pts = []
            for i in range(len(stroke) - 1):
                p1 = stroke[i]
                p2 = stroke[i + 1]
                for t in np.linspace(0, 1, 15):
                    dense_pts.append((int(p1[0] + t * (p2[0] - p1[0])), int(p1[1] + t * (p2[1] - p1[1]))))

            best_letter, best_score, breakdown = self.recognizer.recognize(dense_pts)

            # Check that trajectory score is non-zero
            p_score = breakdown[expected_letter]["path"]
            img_score = breakdown[expected_letter]["img"]
            tot_score = breakdown[expected_letter]["total"]

            print(f"Target: {expected_letter} -> Predicted: {best_letter} (Score: {best_score}, path={p_score}, img={img_score})")

            self.assertGreater(p_score, 0.05, f"Trajectory score for {expected_letter} must not be zero!")
            self.assertGreater(img_score, 0.05, f"Image score for {expected_letter} must not be zero!")
            self.assertEqual(best_letter, expected_letter, f"Expected {expected_letter}, got {best_letter}")

    def test_hud_rendering(self):
        """Verify HUD renders on frame without exceptions."""
        dummy_frame = np.zeros((config.FRAME_HEIGHT, config.FRAME_WIDTH, 3), dtype=np.uint8)
        rendered = self.hud.render_hud(
            frame=dummy_frame,
            mode_name="MOUSE",
            fingers=[0, 1, 0, 0, 0],
            last_letter="W",
            last_score=0.85,
            last_action="Move Cursor",
            fps=30.0,
            is_writing=False,
        )
        self.assertEqual(rendered.shape, (config.FRAME_HEIGHT, config.FRAME_WIDTH, 3))


if __name__ == "__main__":
    unittest.main()
