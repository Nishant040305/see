"""Configuration settings for SEE command helper."""

from pathlib import Path

# Configuration
CONFIG_DIR = Path.home() / '.config' / 'see-helper'
COMMANDS_FILE = CONFIG_DIR / 'commands.json'
