"""History file parsing and import utilities."""

import os
from pathlib import Path
from typing import List, Optional, Set


# Common trivial commands to filter out
TRIVIAL_COMMANDS: Set[str] = {
    'ls', 'll', 'la', 'l',
    'cd', 'cd ..', 'cd ~', 'cd -',
    'pwd', 'clear', 'cls',
    'exit', 'logout',
    'history', 'h',
    'git status', 'gs', 'gst',
    'git diff', 'gd',
    'git log', 'gl',
    'cat', 'less', 'more',
    'vim', 'vi', 'nano', 'emacs',
    'top', 'htop',
    'man', 'help',
    'echo', 'printf',
    'whoami', 'id',
    'date', 'cal',
}


def get_history_file() -> Optional[Path]:
    """
    Detect the current shell and return the history file path.
    
    Returns:
        Path to history file, or None if not found
    """
    shell = os.environ.get('SHELL', '')
    home = Path.home()
    
    if 'zsh' in shell:
        zsh_history = home / '.zsh_history'
        if zsh_history.exists():
            return zsh_history
    
    if 'bash' in shell:
        bash_history = home / '.bash_history'
        if bash_history.exists():
            return bash_history
    
    # Try common locations
    for filename in ['.zsh_history', '.bash_history', '.history']:
        path = home / filename
        if path.exists():
            return path
    
    return None


def read_history(path: Path, lines: int = 100) -> List[str]:
    """
    Read the last N lines from a history file.
    
    Args:
        path: Path to history file
        lines: Number of lines to read from the end
        
    Returns:
        List of command strings (deduplicated, newest first)
    """
    try:
        with open(path, 'r', errors='ignore') as f:
            all_lines = f.readlines()
    except Exception:
        return []
    
    # Process lines (handle zsh history format with timestamps)
    commands = []
    seen = set()
    
    for line in reversed(all_lines[-lines * 2:]):  # Read more to account for multi-line
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Handle zsh extended history format: : timestamp:0;command
        if line.startswith(':') and ';' in line:
            line = line.split(';', 1)[1]
        
        # Skip duplicates
        if line in seen:
            continue
        seen.add(line)
        
        commands.append(line)
        
        if len(commands) >= lines:
            break
    
    return commands


def filter_trivial(commands: List[str], min_length: int = 3) -> List[str]:
    """
    Filter out trivial/common commands.
    
    Args:
        commands: List of commands
        min_length: Minimum command length to keep
        
    Returns:
        Filtered list of commands
    """
    filtered = []
    
    for cmd in commands:
        # Skip short commands
        if len(cmd) < min_length:
            continue
        
        # Skip commands that are just the trivial command
        base_cmd = cmd.split()[0] if cmd.split() else cmd
        if cmd.lower() in TRIVIAL_COMMANDS or base_cmd.lower() in TRIVIAL_COMMANDS:
            continue
        
        # Skip commands starting with trivial commands (like 'cd /path')
        if cmd.lower().startswith('cd ') and len(cmd) < 20:
            continue
        
        filtered.append(cmd)
    
    return filtered
