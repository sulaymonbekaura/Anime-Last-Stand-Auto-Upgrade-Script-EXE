"""Configuration settings for the Anime Last Stand automation demonstration."""

# Hotkey settings
HOTKEY_START = "f5"
HOTKEY_STOP = "f6"
HOTKEY_PAUSE = "f7"

# Delay settings (in seconds)
DELAY_PLACE_UNIT = 0.3
DELAY_UPGRADE = 0.5
DELAY_MERGE = 0.8
DELAY_WAVE_ADVANCE = 1.0
DELAY_SCAN = 0.2

# Screen scanner settings
SCAN_REGION = (0, 0, 1920, 1080)
CONFIDENCE_THRESHOLD = 0.85
UNIT_TEMPLATE_DIR = "templates/"

# Upgrade patterns
UPGRADE_PRIORITY = ["legendary", "epic", "rare", "common"]
MAX_UPGRADE_LEVEL = 5

# Merge settings
MERGE_ENABLED = True
MERGE_SAME_TIER_ONLY = True
MIN_UNITS_FOR_MERGE = 3

# Farm settings
FARM_ENABLED = True
FARM_TARGET_WAVES = 50
RESOURCE_CHECK_INTERVAL = 5.0
