"""Utility functions for logging, privilege checks, and helpers."""

import logging
import sys


def setup_logger(name: str = "als_automation", level: int = logging.INFO) -> logging.Logger:
    """Initialize and return a configured logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger


def check_admin_privileges() -> bool:
    """Check if the script is running with administrator privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except (AttributeError, OSError):
        return False


def validate_dependencies() -> list:
    """Validate that all required dependencies are installed."""
    missing = []
    required = ["keyboard", "pyautogui", "cv2", "PIL", "numpy"]
    for mod in required:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    return missing


def safe_sleep(seconds: float):
    """Sleep with interrupt check for graceful shutdown."""
    import time
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        raise
