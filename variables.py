"""Variable/placeholder handling for commands."""

import re
from typing import List, Dict, Tuple


# Pattern to match {{variable_name}} placeholders
PLACEHOLDER_PATTERN = re.compile(r'\{\{(\w+)\}\}')


def find_placeholders(command: str) -> List[str]:
    """
    Find all placeholders in a command.
    
    Args:
        command: Command string possibly containing {{var}} placeholders
        
    Returns:
        List of placeholder names (without braces), in order of appearance
    """
    matches = PLACEHOLDER_PATTERN.findall(command)
    # Preserve order, remove duplicates
    seen = set()
    result = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            result.append(m)
    return result


def substitute(command: str, values: Dict[str, str]) -> str:
    """
    Substitute placeholders with their values.
    
    Args:
        command: Command with {{var}} placeholders
        values: Dict mapping placeholder names to values
        
    Returns:
        Command with placeholders replaced
    """
    def replace(match):
        name = match.group(1)
        return values.get(name, match.group(0))  # Keep original if not found
    
    return PLACEHOLDER_PATTERN.sub(replace, command)


def substitute_positional(command: str, args: List[str]) -> str:
    """
    Substitute placeholders with positional arguments.
    
    Args:
        command: Command with {{var}} placeholders
        args: List of values in order of placeholder appearance
        
    Returns:
        Command with placeholders replaced
    """
    placeholders = find_placeholders(command)
    values = {}
    for i, name in enumerate(placeholders):
        if i < len(args):
            values[name] = args[i]
    return substitute(command, values)


def prompt_for_values(placeholders: List[str]) -> Dict[str, str]:
    """
    Prompt user interactively for placeholder values.
    
    Args:
        placeholders: List of placeholder names
        
    Returns:
        Dict mapping names to user-provided values
    """
    values = {}
    for name in placeholders:
        try:
            value = input(f"  {name}: ")
            values[name] = value
        except (EOFError, KeyboardInterrupt):
            print()
            return {}
    return values


def has_placeholders(command: str) -> bool:
    """Check if command contains any placeholders."""
    return bool(PLACEHOLDER_PATTERN.search(command))
