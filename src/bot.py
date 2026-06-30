"""Core bot module for auto-placement, auto-merge, auto-upgrade, and auto-wave logic."""

import time
import logging
import pyautogui

logger = logging.getLogger("als_automation.bot")


class Bot:
    """Main automation bot class coordinating all game actions.

    This class manages the primary automation loop, dispatching actions
    for unit placement, upgrading, merging, and wave advancement based
    on screen state detected by the ScreenScanner module.
    """

    def __init__(self, config: dict, scanner=None):
        """Initialize the bot with configuration and an optional scanner.

        Args:
            config: Dictionary of configuration settings.
            scanner: ScreenScanner instance for game element detection.
        """
        self.config = config
        self.scanner = scanner
        self.running = False
        self.paused = False
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1

    def start(self):
        """Start the automation loop."""
        self.running = True
        self.paused = False
        logger.info("Bot started")
        self._main_loop()

    def stop(self):
        """Stop the automation loop."""
        self.running = False
        logger.info("Bot stopped")

    def toggle_pause(self):
        """Toggle the pause state of the bot."""
        self.paused = not self.paused
        state = "paused" if self.paused else "resumed"
        logger.info(f"Bot {state}")

    def _main_loop(self):
        """Main automation loop executing all actions in sequence.

        The loop runs continuously until stop() is called. Each iteration
        performs placement, upgrade, merge, and wave checks with configured
        delays between actions.
        """
        while self.running:
            if self.paused:
                time.sleep(0.5)
                continue
            try:
                self._auto_place()
                self._auto_upgrade()
                self._auto_merge()
                self._auto_wave()
                time.sleep(self.config.get("DELAY_SCAN", 0.2))
            except pyautogui.FailSafeException:
                logger.warning("Fail-safe triggered (mouse moved to corner)")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1.0)

    def _auto_place(self):
        """Automatically place units on the game board.

        Detects an available unit slot and clicks it, then clicks a
        configured board position to place the unit.
        """
        if not self.config.get("AUTO_PLACE_ENABLED", True):
            return
        if self.scanner is None:
            return

        screen = self.scanner.capture_screen()
        if screen.size == 0:
            return

        slot_loc = self.scanner.find_element(screen, "unit_slot")
        if slot_loc:
            pyautogui.click(slot_loc[0], slot_loc[1])
            board_center = self.config.get("PLACE_POSITION", (960, 540))
            pyautogui.click(board_center[0], board_center[1])
            logger.debug("Placed unit on board")
            time.sleep(self.config.get("DELAY_PLACE_UNIT", 0.3))

    def _auto_upgrade(self):
        """Automatically upgrade units based on priority settings.

        Clicks the upgrade button up to MAX_UPGRADE_LEVEL times when
        a unit is selected and the upgrade button is detected.
        """
        if not self.config.get("AUTO_UPGRADE_ENABLED", True):
            return
        if self.scanner is None:
            return

        screen = self.scanner.capture_screen()
        if screen.size == 0:
            return

        upgrade_btn = self.scanner.find_element(screen, "upgrade_button")
        if upgrade_btn:
            max_level = self.config.get("MAX_UPGRADE_LEVEL", 5)
            for _ in range(max_level):
                pyautogui.click(upgrade_btn[0], upgrade_btn[1])
                time.sleep(self.config.get("DELAY_UPGRADE", 0.5))
            logger.debug(f"Upgraded unit to level {max_level}")

    def _auto_merge(self):
        """Automatically merge duplicate units for tier progression.

        Checks for a merge trigger on screen and clicks the merge
        button when available, respecting configured merge rules.
        """
        if not self.config.get("MERGE_ENABLED", True):
            return
        if self.scanner is None:
            return

        screen = self.scanner.capture_screen()
        if screen.size == 0:
            return

        if self.scanner.detect_merge_trigger(screen):
            merge_btn = self.scanner.find_element(screen, "merge_button")
            if merge_btn:
                pyautogui.click(merge_btn[0], merge_btn[1])
                time.sleep(self.config.get("DELAY_MERGE", 0.8))
                logger.debug("Merged units")

    def _auto_wave(self):
        """Automatically advance to the next wave.

        When no active wave is detected, clicks the next wave button
        to progress the game automatically.
        """
        if not self.config.get("AUTO_WAVE_ENABLED", True):
            return
        if self.scanner is None:
            return

        screen = self.scanner.capture_screen()
        if screen.size == 0:
            return

        status = self.scanner.detect_wave_status(screen)
        if not status["active"]:
            next_btn = self.scanner.find_element(screen, "next_wave_button")
            if next_btn:
                pyautogui.click(next_btn[0], next_btn[1])
                time.sleep(self.config.get("DELAY_WAVE_ADVANCE", 1.0))
                logger.debug("Advanced to next wave")
