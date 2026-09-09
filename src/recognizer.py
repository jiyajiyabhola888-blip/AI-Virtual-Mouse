"""
Letter Recognizer module for Air-Writing.
Combines 88% Trajectory/Path Analysis (resampling, Euclidean distance, tangent vector direction similarity)
with 12% Image/Template Matching.
Guarantees non-zero trajectory scores and selects the best-matching letter among [W, Y, G, I, C, N].
"""
import math
import os
from pathlib import Path
import cv2
import numpy as np
from src import config


class LetterRecognizer:
    """
    Recognizes drawn air-writing letters using dual trajectory and template matching.
    """

    def __init__(self):
        self.supported_letters = config.SUPPORTED_LETTERS
        self.resample_n = config.RESAMPLE_POINTS
        self.canvas_size = config.CANVAS_SIZE
        self.templates_dir = Path(config.TEMPLATES_DIR)

        # Build / generate reference canonical trajectories
        self.reference_trajectories = self._build_canonical_trajectories()

        # Ensure template images exist or generate them
        self._ensure_templates()

        # Load template images into memory
        self.template_images = self._load_templates()

    # --------------------------------------------------
    # CANONICAL REFERENCE TRAJECTORIES
    # --------------------------------------------------
    def _build_canonical_trajectories(self) -> dict[str, list[np.ndarray]]:
        """
        Constructs normalized canonical reference polylines for W, Y, G, I, C, N.
        Supports single-stroke and natural air-writing flow variations.
        Each polyline is defined in normalized coordinates [-1.0, 1.0].
        """
        raw_refs: dict[str, list[list[tuple[float, float]]]] = {
            # 'W': Top-Left -> Bottom-Left -> Center-Top -> Bottom-Right -> Top-Right
            "W": [
                [
                    (-0.85, -0.85),
                    (-0.45, 0.85),
                    (0.00, -0.20),
                    (0.45, 0.85),
                    (0.85, -0.85),
                ],
                # Smooth rounded W
                [
                    (-0.80, -0.80),
                    (-0.50, 0.90),
                    (-0.30, 0.90),
                    (0.00, -0.10),
                    (0.30, 0.90),
                    (0.50, 0.90),
                    (0.80, -0.80),
                ],
            ],
            # 'Y': Top-Left -> Center-Junction -> Bottom-Tail (or single continuous fork)
            "Y": [
                [
                    (-0.75, -0.85),
                    (0.00, 0.05),
                    (0.00, 0.90),
                    (0.00, 0.05),
                    (0.75, -0.85),
                ],
                # Cursive / continuous single-stroke Y: Left branch -> Right branch -> Down stem
                [
                    (-0.70, -0.80),
                    (-0.15, -0.10),
                    (0.70, -0.80),
                    (0.00, -0.05),
                    (0.00, 0.90),
                ],
            ],
            # 'G': Top-Right -> Top-Left arc -> Bottom arc -> Inward horizontal bar
            "G": [
                [
                    (0.70, -0.65),
                    (0.10, -0.90),
                    (-0.75, -0.55),
                    (-0.85, 0.10),
                    (-0.60, 0.80),
                    (0.20, 0.90),
                    (0.75, 0.60),
                    (0.75, 0.05),
                    (0.10, 0.05),
                ],
                [
                    (0.80, -0.70),
                    (0.00, -0.95),
                    (-0.80, -0.40),
                    (-0.80, 0.40),
                    (0.00, 0.95),
                    (0.80, 0.70),
                    (0.80, 0.10),
                    (0.20, 0.10),
                ],
            ],
            # 'I': Straight vertical downward stroke (or with crossbars)
            "I": [
                [
                    (0.00, -0.90),
                    (0.00, -0.30),
                    (0.00, 0.30),
                    (0.00, 0.90),
                ],
                # 'I' with subtle top-to-bottom natural angle
                [
                    (-0.05, -0.85),
                    (0.00, 0.00),
                    (0.05, 0.85),
                ],
            ],
            # 'C': Top-Right -> Upper Curve -> Left Spine -> Lower Curve -> Bottom-Right
            "C": [
                [
                    (0.80, -0.75),
                    (0.15, -0.90),
                    (-0.75, -0.50),
                    (-0.85, 0.00),
                    (-0.75, 0.50),
                    (0.15, 0.90),
                    (0.80, 0.75),
                ],
                [
                    (0.75, -0.80),
                    (0.00, -0.95),
                    (-0.80, -0.35),
                    (-0.80, 0.35),
                    (0.00, 0.95),
                    (0.75, 0.80),
                ],
            ],
            # 'N': Bottom-Left -> Top-Left -> Bottom-Right -> Top-Right (or Top-Left start)
            "N": [
                [
                    (-0.75, 0.85),
                    (-0.75, -0.85),
                    (0.75, 0.85),
                    (0.75, -0.85),
                ],
                # Top-Left start: Top-Left -> Bottom-Left -> Top-Right -> Bottom-Right
                [
                    (-0.75, -0.85),
                    (-0.75, 0.85),
                    (0.75, -0.85),
                    (0.75, 0.85),
                ],
            ],
        }

        # Normalize and resample each reference variant to N=64 points
        normalized_refs: dict[str, list[np.ndarray]] = {}
        for letter, variants in raw_refs.items():
            normalized_refs[letter] = []
            for var in variants:
                resampled = self.resample_polyline(var, self.resample_n)
                norm_pts = self.normalize_points(resampled)
                normalized_refs[letter].append(norm_pts)

        return normalized_refs

    # --------------------------------------------------
    # TRAJECTORY NORMALIZATION & RESAMPLING
    # --------------------------------------------------
    def resample_polyline(
        self,
        points: list[tuple[float, float]] | np.ndarray,
        target_n: int = 64,
    ) -> np.ndarray:
        """
        Resamples an arbitrary polyline into `target_n` equidistant points along the arc length.
        """
        pts = np.array(points, dtype=np.float32)
        if len(pts) == 0:
            return np.zeros((target_n, 2), dtype=np.float32)
        if len(pts) == 1:
            return np.repeat(pts, target_n, axis=0)

        # Compute cumulative distance along the curve
        diffs = np.diff(pts, axis=0)
        seg_lengths = np.hypot(diffs[:, 0], diffs[:, 1])
        cum_dist = np.insert(np.cumsum(seg_lengths), 0, 0.0)
        total_length = cum_dist[-1]

        if total_length <= 1e-6:
            return np.repeat(pts[:1], target_n, axis=0)

        # Generate equidistant sample distances
        sample_dists = np.linspace(0.0, total_length, target_n)

        # Interpolate X and Y coordinates
        new_x = np.interp(sample_dists, cum_dist, pts[:, 0])
        new_y = np.interp(sample_dists, cum_dist, pts[:, 1])

        return np.column_stack((new_x, new_y)).astype(np.float32)

    def normalize_points(self, points: np.ndarray) -> np.ndarray:
        """
        Centers points at (0, 0) and scales them uniformly to [-1, 1] while preserving aspect ratio.
        """
        if len(points) == 0:
            return points

        pts = np.array(points, dtype=np.float32)
        min_xy = pts.min(axis=0)
        max_xy = pts.max(axis=0)
        span = max_xy - min_xy
        max_span = max(span[0], span[1], 1e-5)

        # Center to origin
        centroid = (min_xy + max_xy) / 2.0
        centered = pts - centroid

        # Scale to [-1, 1]
        scaled = centered / (max_span / 1.8)
        return scaled.astype(np.float32)

    # --------------------------------------------------
    # TRAJECTORY SCORING ALGORITHM
    # --------------------------------------------------
    def compute_trajectory_score(self, user_points: np.ndarray, ref_points: np.ndarray) -> float:
        """
        Calculates mathematical similarity [0.0, 1.0] between normalized user stroke and reference.
        Combines:
          1. Point-to-point Euclidean distance similarity
          2. Tangent direction cosine similarity
          3. Start/End point proximity
        """
        # 1. Point Distance Metric
        dists = np.hypot(user_points[:, 0] - ref_points[:, 0], user_points[:, 1] - ref_points[:, 1])
        mean_dist = float(np.mean(dists))
        # Distance decay score: exp(-mean_dist * 1.5)
        dist_score = math.exp(-mean_dist * 1.5)

        # 2. Tangent Direction Cosine Similarity
        user_diff = np.diff(user_points, axis=0)
        ref_diff = np.diff(ref_points, axis=0)

        user_lens = np.hypot(user_diff[:, 0], user_diff[:, 1]) + 1e-6
        ref_lens = np.hypot(ref_diff[:, 0], ref_diff[:, 1]) + 1e-6

        user_dirs = user_diff / user_lens[:, None]
        ref_dirs = ref_diff / ref_lens[:, None]

        # Dot product of unit direction vectors along the stroke
        cos_sims = np.sum(user_dirs * ref_dirs, axis=1)
        # Map cosine [-1, 1] to [0, 1]
        dir_score = float(np.mean(np.clip((cos_sims + 1.0) / 2.0, 0.0, 1.0)))

        # 3. Start & End Landmark Proximity
        start_dist = float(np.hypot(user_points[0, 0] - ref_points[0, 0], user_points[0, 1] - ref_points[0, 1]))
        end_dist = float(np.hypot(user_points[-1, 0] - ref_points[-1, 0], user_points[-1, 1] - ref_points[-1, 1]))
        boundary_score = math.exp(-(start_dist + end_dist) * 0.8)

        # Combined Trajectory Score
        traj_score = 0.50 * dist_score + 0.35 * dir_score + 0.15 * boundary_score
        return float(np.clip(traj_score, 0.05, 0.99))

    def evaluate_all_trajectories(self, user_points: np.ndarray) -> dict[str, float]:
        """
        Evaluates user stroke against all supported letters' canonical trajectories.
        Returns dict of {letter: best_path_score}.
        """
        scores: dict[str, float] = {}
        for letter in self.supported_letters:
            variants = self.reference_trajectories.get(letter, [])
            var_scores = [self.compute_trajectory_score(user_points, ref) for ref in variants]
            scores[letter] = max(var_scores) if var_scores else 0.10
        return scores

    # --------------------------------------------------
    # TEMPLATE IMAGE MANAGEMENT & SCORING
    # --------------------------------------------------
    def _ensure_templates(self):
        """Generates starter template PNGs in templates/ if any are missing."""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        size = self.canvas_size

        for letter in self.supported_letters:
            filepath = self.templates_dir / f"{letter}.png"
            if not filepath.exists():
                # Create clean black canvas with thick white letter
                img = np.zeros((size, size), dtype=np.uint8)
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 3.2
                thickness = 9

                # Measure text size to center it
                (text_w, text_h), baseline = cv2.getTextSize(letter, font, font_scale, thickness)
                x = (size - text_w) // 2
                y = (size + text_h) // 2 - 4

                cv2.putText(
                    img,
                    letter,
                    (x, y),
                    font,
                    font_scale,
                    255,
                    thickness,
                    lineType=cv2.LINE_AA,
                )
                cv2.imwrite(str(filepath), img)
                print(f"[INFO] Generated starter template: {filepath.name}")

    def _load_templates(self) -> dict[str, np.ndarray]:
        """Loads all template PNGs from templates/ into memory."""
        templates = {}
        for letter in self.supported_letters:
            filepath = self.templates_dir / f"{letter}.png"
            if filepath.exists():
                img = cv2.imread(str(filepath), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    if img.shape != (self.canvas_size, self.canvas_size):
                        img = cv2.resize(img, (self.canvas_size, self.canvas_size))
                    templates[letter] = img
        return templates

    def render_trajectory_to_image(self, points: np.ndarray) -> np.ndarray:
        """
        Renders normalized [-1, 1] trajectory to a binary canvas image.
        """
        size = self.canvas_size
        img = np.zeros((size, size), dtype=np.uint8)
        if len(points) < 2:
            return img

        # Map [-1, 1] to pixel coordinates [16, size - 16]
        margin = 18
        span = size - 2 * margin
        px = ((points[:, 0] + 1.0) / 2.0 * span + margin).astype(np.int32)
        py = ((points[:, 1] + 1.0) / 2.0 * span + margin).astype(np.int32)

        for i in range(1, len(points)):
            cv2.line(
                img,
                (px[i - 1], py[i - 1]),
                (px[i], py[i]),
                255,
                7,
                lineType=cv2.LINE_AA,
            )

        return img

    def compute_image_scores(self, user_img: np.ndarray) -> dict[str, float]:
        """
        Matches rendered user drawing image against template images.
        """
        scores: dict[str, float] = {}
        user_blur = cv2.GaussianBlur(user_img, (5, 5), 0)

        for letter in self.supported_letters:
            tmpl = self.template_images.get(letter)
            if tmpl is None:
                scores[letter] = 0.20
                continue

            tmpl_blur = cv2.GaussianBlur(tmpl, (5, 5), 0)

            # 1. Normalized Cross-Correlation
            res = cv2.matchTemplate(user_blur, tmpl_blur, cv2.TM_CCOEFF_NORMED)
            ncc_score = float(res[0][0]) if res.size > 0 else 0.0
            ncc_norm = max(0.0, (ncc_score + 1.0) / 2.0)

            # 2. Overlap / Intersection score
            intersection = np.sum((user_blur > 50) & (tmpl_blur > 50))
            union = np.sum((user_blur > 50) | (tmpl_blur > 50)) + 1e-6
            iou_score = float(intersection / union)

            # Blended Image Score
            blended = 0.55 * ncc_norm + 0.45 * iou_score
            scores[letter] = float(np.clip(blended, 0.05, 0.99))

        return scores

    # --------------------------------------------------
    # MAIN RECOGNITION PIPELINE
    # --------------------------------------------------
    def recognize(self, raw_points: list[tuple[int, int]]) -> tuple[str, float, dict[str, dict[str, float]]]:
        """
        Recognizes the drawn letter from raw air-writing points.
        Returns:
            best_letter: e.g. 'W'
            best_score: e.g. 0.845
            breakdown: dict of detailed scores for each letter
        """
        if len(raw_points) < config.MIN_DRAWING_POINTS:
            # Fallback for empty/sparse drawings
            return "W", 0.10, {
                ltr: {"path": 0.10, "img": 0.10, "total": 0.10} for ltr in self.supported_letters
            }

        # 1. Resample and Normalize
        resampled = self.resample_polyline(raw_points, self.resample_n)
        normalized_pts = self.normalize_points(resampled)

        # 2. Trajectory Scores (88% weight)
        path_scores = self.evaluate_all_trajectories(normalized_pts)

        # 3. Image Template Scores (12% weight)
        user_img = self.render_trajectory_to_image(normalized_pts)
        img_scores = self.compute_image_scores(user_img)

        # 4. Combine Weighted Scores
        breakdown: dict[str, dict[str, float]] = {}
        best_letter = self.supported_letters[0]
        best_score = -1.0

        for letter in self.supported_letters:
            p_score = path_scores.get(letter, 0.10)
            i_score = img_scores.get(letter, 0.10)
            total = (config.TRAJECTORY_WEIGHT * p_score) + (config.IMAGE_WEIGHT * i_score)

            breakdown[letter] = {
                "path": round(p_score, 3),
                "img": round(i_score, 3),
                "total": round(total, 3),
            }

            if total > best_score:
                best_score = total
                best_letter = letter

        # 5. Formatted Console Logging (per requirement Section 15)
        print("============================================================")
        print("[LETTER RECOGNITION]")
        for letter in self.supported_letters:
            b = breakdown[letter]
            print(f"{letter}: {b['total']:.3f}  (path={b['path']:.3f}, img={b['img']:.3f})")
        print(f"\n[BEST] {best_letter} = {best_score:.3f}")
        print("============================================================")

        return best_letter, round(best_score, 3), breakdown
