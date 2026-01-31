"""Pretty printing for commands and statistics."""

from typing import Dict, List
import textwrap
import shutil


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
        if cmd.get('alias'):
            print(f"    Alias: {cmd['alias']}")
        if verbose:
            print(f"    Used: {cmd.get('used_count', 0)} times")
    
    @staticmethod
    def print_stats(stats: Dict):
        """Print statistics."""
        print(f"\n Statistics")
        print(f"   Total commands: {stats['total']}")
        print(f"   Unique tags: {stats['unique_tags']}")
        if stats['tags']:
            print(f"   Tags: {', '.join(stats['tags'])}")
        
        if stats['most_used']:
            print(f"\n   Most used commands:")
            for cmd in stats['most_used']:
                print(f"   - [{cmd['id']}] {cmd['description']} ({cmd['used_count']} uses)")

    @staticmethod
    def print_table(commands: List[Dict]):
        """Print commands in a table format with text wrapping."""
        if not commands:
            return

        # Define fixed column widths
        # Get terminal width to adjust command column if needed, but keep it simple for now
        # ID | Desc | Command | Tags
        term_width = shutil.get_terminal_size((120, 20)).columns
        
        id_width = 4
        alias_width = 10
        desc_width = 25
        tags_width = 20
        # Remaining width for command (accounting for separators ' | ' and padding)
        # Separators: 4 * 2 chars = 8 chars approx
        # Margins: 2 chars
        static_width = id_width + alias_width + desc_width + tags_width + 12
        cmd_width = max(25, term_width - static_width)
        
        headers = ["ID", "Alias", "Description", "Command", "Tags"]
        widths = [id_width, alias_width, desc_width, cmd_width, tags_width]
        
        # Print header
        header_row = ""
        for h, w in zip(headers, widths):
            header_row += h.ljust(w) + "  "
        
        print("\n" + header_row)
        print("-" * len(header_row))
        
        # Print rows
        for cmd in commands:
            tags_str = ', '.join(cmd.get('tags', []))
            
            # Wrap content
            col_data = [
                str(cmd['id']),
                cmd.get('alias') or "",
                cmd['description'] or "",
                cmd['command'],
                tags_str
            ]
            
            wrapped_cols = []
            max_lines = 1
            
            for i, data in enumerate(col_data):
                # Use simple splitting for ID, others use textwrap
                if i == 0:
                    lines = [data]
                else:
                    lines = textwrap.wrap(data, width=widths[i])
                    if not lines: # Handle empty string
                        lines = [""]
                
                wrapped_cols.append(lines)
                max_lines = max(max_lines, len(lines))
            
            # Print lines for this row
            for line_idx in range(max_lines):
                row_str = ""
                for col_idx, lines in enumerate(wrapped_cols):
                    if line_idx < len(lines):
                        cell = lines[line_idx]
                    else:
                        cell = ""
                    row_str += cell.ljust(widths[col_idx]) + "  "
                print(row_str)
            
            # Spacing between rows
            print()
