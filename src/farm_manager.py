"""Farm manager module for resource accumulation and free unit collection."""

import time
import logging
import pyautogui

logger = logging.getLogger("als_automation.farm")


class FarmManager:
    """Manages automated farming of resources and free unit claims.

    This class coordinates resource collection, free unit claiming, and
    milestone reward checks as part of the overall farming cycle.
    It tracks statistics such as resources collected, units claimed,
    and waves completed.
    """

    def __init__(self, config: dict, scanner=None):
        """Initialize the farm manager with configuration and optional scanner.

        Args:
            config: Dictionary of configuration settings.
            scanner: ScreenScanner instance for game element detection.
        """
        self.config = config
        self.scanner = scanner
        self.resources_collected = 0
        self.units_claimed = 0
        self.waves_completed = 0
        self.target_waves = config.get("FARM_TARGET_WAVES", 50)

    def run_farm_cycle(self) -> bool:
        """Execute a complete farming cycle.

        Performs resource collection, free unit claims, and milestone
        checks in sequence, then increments the wave counter.

        Returns:
            True if the target wave count has been reached, False otherwise.
        """
        if self.waves_completed >= self.target_waves:
            logger.info(f"Farm target reached: {self.target_waves} waves")
            return True

        self._collect_resources()
        self._claim_free_units()
        self._check_milestones()
        self.waves_completed += 1
        logger.info(f"Farm cycle {self.waves_completed}/{self.target_waves} complete")
        return self.waves_completed >= self.target_waves

    def _collect_resources(self):
        """Scan for and collect dropped resources on screen.

        Looks for gold, gem, and XP resource templates and clicks
        each detected position to collect them.
        """
        if self.scanner is None:
            return

        screen = self.scanner.capture_screen()
        if screen.size == 0:
            return

        resource_positions = []
        for tpl in ["resource_gold", "resource_gem", "resource_xp"]:
            pos = self.scanner.find_element(screen, tpl)
            if pos:
                resource_positions.append(pos)

        for pos in resource_positions:
            pyautogui.click(pos[0], pos[1])
            self.resources_collected += 1
            time.sleep(0.15)

        if resource_positions:
            logger.debug(f"Collected {len(resource_positions)} resource drops")

    def _claim_free_units(self):
        """Claim any available free units from rewards or events.

        Detects the free claim button on screen and clicks it to
        add free units to the inventory.
        """
        if self.scanner is None:
            return

        screen = self.scanner.capture_screen()
        if screen.size == 0:
            return

        claim_btn = self.scanner.find_element(screen, "free_claim_button")
        if claim_btn:
            pyautogui.click(claim_btn[0], claim_btn[1])
            self.units_claimed += 1
            time.sleep(0.3)
            logger.debug("Claimed a free unit reward")

    def _check_milestones(self):
        """Check and claim milestone rewards if available.

        Scans for a milestone reward button and clicks it when
        detected to collect milestone bonuses.
        """
        if self.scanner is None:
            return

        screen = self.scanner.capture_screen()
        if screen.size == 0:
            return

        milestone_btn = self.scanner.find_element(screen, "milestone_reward")
        if milestone_btn:
            pyautogui.click(milestone_btn[0], milestone_btn[1])
            time.sleep(0.5)
            logger.debug("Claimed milestone reward")

    def get_stats(self) -> dict:
        """Return current farming statistics.

        Returns:
            Dictionary with resources_collected, units_claimed,
            waves_completed, target_waves, and progress_percent.
        """
        return {
            "resources_collected": self.resources_collected,
            "units_claimed": self.units_claimed,
            "waves_completed": self.waves_completed,
            "target_waves": self.target_waves,
            "progress_percent": round(self.waves_completed / self.target_waves * 100, 1)
        }

    def reset_stats(self):
        """Reset all farming counters to zero."""
        self.resources_collected = 0
        self.units_claimed = 0
        self.waves_completed = 0
        logger.info("Farm statistics reset")
