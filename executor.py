"""Command execution layer."""

import sys
from typing import Tuple


class CommandExecutor:
    """Handles command execution."""
    
    @staticmethod
    def execute(command: str, shell_mode: bool = False) -> Tuple[bool, int]:
        """
        Execute a command.
        
        Args:
            command: The command to execute
            shell_mode: If True, print command for shell evaluation instead of executing
            
        Returns:
            Tuple of (success, return_code)
        """
        if shell_mode:
            # Print command for shell wrapper to evaluate
            print(command)
            return True, 0
        else:
            import subprocess
            try:
                result = subprocess.run(command, shell=True, text=True)
                return result.returncode == 0, result.returncode
            except Exception as e:
                print(f"✗ Error executing command: {e}", file=sys.stderr)
                return False, 1
