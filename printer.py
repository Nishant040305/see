"""Pretty printing for commands and statistics."""

from typing import Dict


class CommandPrinter:
    """Handles pretty printing of commands."""
    
    @staticmethod
    def print_command(cmd: Dict, verbose: bool = True):
        """Pretty print a single command."""
        tags_str = ', '.join(f"#{tag}" for tag in cmd['tags'])
        print(f"\n[{cmd['id']}] {cmd['description']}")
        print(f"    Command: {cmd['command']}")
        if tags_str:
            print(f"    Tags: {tags_str}")
        if verbose:
            print(f"    Used: {cmd.get('used_count', 0)} times")
    
    @staticmethod
    def print_stats(stats: Dict):
        """Print statistics."""
        print(f"\n📊 Statistics")
        print(f"   Total commands: {stats['total']}")
        print(f"   Unique tags: {stats['unique_tags']}")
        if stats['tags']:
            print(f"   Tags: {', '.join(stats['tags'])}")
        
        if stats['most_used']:
            print(f"\n   Most used commands:")
            for cmd in stats['most_used']:
                print(f"   - [{cmd['id']}] {cmd['description']} ({cmd['used_count']} uses)")
