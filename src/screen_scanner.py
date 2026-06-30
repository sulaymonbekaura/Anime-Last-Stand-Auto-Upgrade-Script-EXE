"""Screen scanning module for detecting game elements and unit positions."""

import logging
import numpy as np
import cv2
from PIL import ImageGrab

logger = logging.getLogger("als_automation.scanner")


class ScreenScanner:
    """Handles screen capture and template matching for game element detection."""

    def __init__(self, scan_region=None, confidence=0.85):
        """Initialize the scanner with an optional region and confidence threshold.

        Args:
            scan_region: Tuple of (left, top, right, bottom) for capture area.
            confidence: Minimum match confidence (0.0 to 1.0).
        """
        self.scan_region = scan_region
        self.confidence = confidence
        self.templates = {}

    def load_template(self, name: str, path: str):
        """Load a template image for matching.

        Args:
            name: Identifier for the template.
            path: File path to the template image.
        """
        try:
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is not None:
                self.templates[name] = img
                logger.debug(f"Loaded template: {name}")
            else:
                logger.warning(f"Could not read template image: {path}")
        except Exception as e:
            logger.error(f"Error loading template {name}: {e}")

    def capture_screen(self) -> np.ndarray:
        """Capture the current screen or defined region.

        Returns:
            numpy array of the captured image in BGR format, or empty array on failure.
        """
        try:
            if self.scan_region:
                screenshot = ImageGrab.grab(bbox=self.scan_region)
            else:
                screenshot = ImageGrab.grab()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return np.array([])

    def find_element(self, screen: np.ndarray, template_name: str) -> tuple:
        """Find a template on screen and return its center coordinates.

        Args:
            screen: The captured screen image as numpy array.
            template_name: The identifier of the template to search for.

        Returns:
            Tuple of (center_x, center_y) if found, or None if not found.
        """
        if template_name not in self.templates:
            logger.debug(f"Template not loaded: {template_name}")
            return None

        if screen.size == 0:
            return None

        template = self.templates[template_name]
        if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
            return None

        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= self.confidence:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            logger.debug(f"Found {template_name} at ({center_x}, {center_y}) conf={max_val:.2f}")
            return (center_x, center_y)

        return None

    def detect_unit_positions(self, screen: np.ndarray) -> list:
        """Detect all placed unit positions on the game board.

        Args:
            screen: The captured screen image.

        Returns:
            List of dicts with 'name' and 'position' keys for each detected unit.
        """
        positions = []
        unit_templates = [k for k in self.templates if k.startswith("unit_")]
        for tpl_name in unit_templates:
            loc = self.find_element(screen, tpl_name)
            if loc:
                positions.append({"name": tpl_name, "position": loc})
        logger.debug(f"Detected {len(positions)} units on board")
        return positions

    def detect_merge_trigger(self, screen: np.ndarray) -> bool:
        """Check if a merge action is available on screen.

        Args:
            screen: The captured screen image.

        Returns:
            True if merge button is detected, False otherwise.
        """
        merge_loc = self.find_element(screen, "merge_button")
        return merge_loc is not None

    def detect_wave_status(self, screen: np.ndarray) -> dict:
        """Detect current wave number and enemy count from screen.

        Args:
            screen: The captured screen image.

        Returns:
            Dict with 'active', 'wave_number', and 'enemies_remaining' keys.
        """
        wave_loc = self.find_element(screen, "wave_indicator")
        status = {
            "active": wave_loc is not None,
            "wave_number": 0,
            "enemies_remaining": 0
        }
        # In a full implementation, OCR would extract numeric values here
        return status
