"""Entry point for the Anime Last Stand automation demonstration script."""

import sys
import time
import logging

try:
    import keyboard
except ImportError:
    print("Error: \'keyboard\' module is required. Install with: pip install keyboard")
    sys.exit(1)

from config import *
from bot import Bot
from farm_manager import FarmManager
from screen_scanner import ScreenScanner
from utils import setup_logger, check_admin_privileges, validate_dependencies

logger = setup_logger()


def build_config() -> dict:
    """Build the configuration dictionary from config module constants.

    Returns:
        Dictionary containing all configuration values for the bot and farm manager.
    """
    return {
        "HOTKEY_START": HOTKEY_START,
        "HOTKEY_STOP": HOTKEY_STOP,
        "HOTKEY_PAUSE": HOTKEY_PAUSE,
        "DELAY_PLACE_UNIT": DELAY_PLACE_UNIT,
        "DELAY_UPGRADE": DELAY_UPGRADE,
        "DELAY_MERGE": DELAY_MERGE,
        "DELAY_WAVE_ADVANCE": DELAY_WAVE_ADVANCE,
        "DELAY_SCAN": DELAY_SCAN,
        "SCAN_REGION": SCAN_REGION,
        "CONFIDENCE_THRESHOLD": CONFIDENCE_THRESHOLD,
        "UPGRADE_PRIORITY": UPGRADE_PRIORITY,
        "MAX_UPGRADE_LEVEL": MAX_UPGRADE_LEVEL,
        "AUTO_PLACE_ENABLED": True,
        "AUTO_UPGRADE_ENABLED": True,
        "AUTO_WAVE_ENABLED": True,
        "MERGE_ENABLED": MERGE_ENABLED,
        "MERGE_SAME_TIER_ONLY": MERGE_SAME_TIER_ONLY,
        "MIN_UNITS_FOR_MERGE": MIN_UNITS_FOR_MERGE,
        "FARM_ENABLED": FARM_ENABLED,
        "FARM_TARGET_WAVES": FARM_TARGET_WAVES,
        "RESOURCE_CHECK_INTERVAL": RESOURCE_CHECK_INTERVAL,
        "PLACE_POSITION": (960, 540),
    }


def main():
    """Main function: initialize components and set up hotkey listeners.

    This function validates dependencies, checks admin privileges,
    initializes the screen scanner, bot, and farm manager, registers
    hotkey callbacks, and keeps the main thread alive.
    """
    logger.info("=" * 50)
    logger.info("Anime Last Stand Automation Tool - Educational Demo")
    logger.info("=" * 50)

    # Validate that all required dependencies are installed
    missing = validate_dependencies()
    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.error("Install them with: pip install -r requirements.txt")
        sys.exit(1)

    # Check if running with administrator privileges
    if not check_admin_privileges():
        logger.warning("Not running as administrator. Some features may not work.")

    # Build configuration from module constants
    config = build_config()

    # Initialize the screen scanner for template matching
    scanner = ScreenScanner(
        scan_region=config.get("SCAN_REGION"),
        confidence=config.get("CONFIDENCE_THRESHOLD")
    )
    logger.info("Screen scanner initialized")

    # Initialize the main bot and farm manager
    bot = Bot(config, scanner)
    farm = FarmManager(config, scanner)
    logger.info("Bot and farm manager initialized")

    # Define hotkey callback functions
    def on_start():
        if not bot.running:
            logger.info(f"Starting automation (hotkey: {config['HOTKEY_START']})")
            bot.start()

    def on_stop():
        if bot.running:
            logger.info(f"Stopping automation (hotkey: {config['HOTKEY_STOP']})")
            bot.stop()

    def on_pause():
        bot.toggle_pause()

    # Register hotkeys with the keyboard library
    keyboard.add_hotkey(config["HOTKEY_START"], on_start)
    keyboard.add_hotkey(config["HOTKEY_STOP"], on_stop)
    keyboard.add_hotkey(config["HOTKEY_PAUSE"], on_pause)

    logger.info(
        f"Hotkeys: START={config['HOTKEY_START']}, "
        f"STOP={config['HOTKEY_STOP']}, PAUSE={config['HOTKEY_PAUSE']}"
    )
    logger.info("Press hotkeys to control the automation. Press Ctrl+C to exit.")

    # Keep the main thread alive while the bot runs
    try:
        while True:
            time.sleep(0.5)
            if bot.running and not bot.paused and config.get("FARM_ENABLED"):
                farm.run_farm_cycle()
                time.sleep(config.get("RESOURCE_CHECK_INTERVAL", 5.0))
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        bot.stop()
        keyboard.unhook_all()
        logger.info("Goodbye!")


if __name__ == "__main__":
    main()
