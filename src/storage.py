"""Storage layer for command persistence."""

import json
import sys
from pathlib import Path
from typing import List, Dict


class CommandStorage:
    """Handles storage and retrieval of commands."""
    
    def __init__(self, commands_file: Path):
        self.commands_file = commands_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create commands file if it doesn't exist."""
        self.commands_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.commands_file.exists():
            self.commands_file.write_text('[]')
    
    def load(self) -> List[Dict]:
        """Load commands from JSON file."""
        try:
            with open(self.commands_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Commands file is corrupted. Starting fresh.", file=sys.stderr)
            return []
    
    def save(self, commands: List[Dict]):
        """Save commands to JSON file."""
        with open(self.commands_file, 'w') as f:
            json.dump(commands, f, indent=2)
