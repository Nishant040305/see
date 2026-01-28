"""Interactive TUI for command selection using curses."""

import curses
from typing import List, Dict, Optional


def interactive_select(commands: List[Dict]) -> Optional[int]:
    """
    Display an interactive TUI for selecting a command.
    
    Args:
        commands: List of command dictionaries
        
    Returns:
        The ID of the selected command, or None if cancelled
    """
    if not commands:
        return None
    
    return curses.wrapper(_run_tui, commands)


def _run_tui(stdscr, commands: List[Dict]) -> Optional[int]:
    """Run the curses TUI."""
    curses.curs_set(0)  # Hide cursor
    curses.use_default_colors()
    
    # Initialize colors
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)   # Selected row
    curses.init_pair(2, curses.COLOR_CYAN, -1)                   # ID
    curses.init_pair(3, curses.COLOR_GREEN, -1)                  # Description
    curses.init_pair(4, curses.COLOR_YELLOW, -1)                 # Tags
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Header
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Footer
    curses.init_pair(7, curses.COLOR_MAGENTA, -1)                # Preview label
    
    current_idx = 0
    offset = 0
    
    # Column widths
    COL_ID = 6
    COL_DESC = 20
    COL_CMD = 35
    COL_TAGS = 15
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # ═══════════════════════════════════════════════════════════════
        # Header
        # ═══════════════════════════════════════════════════════════════
        title = " SEE - Command Selector "
        
        try:
            stdscr.addstr(0, 0, "═" * (width - 1), curses.color_pair(5))
            center_pos = max(0, (width - len(title)) // 2)
            stdscr.addstr(0, center_pos, title, curses.color_pair(5) | curses.A_BOLD)
        except curses.error:
            pass
        
        # Calculate layout
        preview_height = 4
        list_height = max(3, height - 3 - preview_height)
        
        # Adjust offset for scrolling
        if current_idx < offset:
            offset = current_idx
        elif current_idx >= offset + list_height:
            offset = current_idx - list_height + 1
        
        # ═══════════════════════════════════════════════════════════════
        # Column Headers
        # ═══════════════════════════════════════════════════════════════
        try:
            header = f"  {'ID':<{COL_ID}} {'Description':<{COL_DESC}} {'Command':<{COL_CMD}} {'Tags':<{COL_TAGS}}"
            stdscr.addstr(1, 0, header[:width-1], curses.A_DIM | curses.A_UNDERLINE)
        except curses.error:
            pass
        
        # ═══════════════════════════════════════════════════════════════
        # Command List
        # ═══════════════════════════════════════════════════════════════
        for i, cmd in enumerate(commands[offset:offset + list_height]):
            actual_idx = i + offset
            y = i + 2
            
            if y >= height - preview_height - 1:
                break
            
            # Format columns
            id_str = f"[{cmd['id']}]"[:COL_ID].ljust(COL_ID)
            desc = (cmd.get('description', '') or '')[:COL_DESC].ljust(COL_DESC)
            command = (cmd.get('command', '') or '')[:COL_CMD].ljust(COL_CMD)
            tags = ', '.join(cmd.get('tags', []))[:COL_TAGS].ljust(COL_TAGS)
            
            # Selection indicator
            indicator = "▶ " if actual_idx == current_idx else "  "
            
            try:
                if actual_idx == current_idx:
                    # Selected row
                    line = f"{indicator}{id_str} {desc} {command} {tags}"
                    stdscr.addstr(y, 0, line[:width-1].ljust(width-1), curses.color_pair(1) | curses.A_BOLD)
                else:
                    # Normal row
                    stdscr.addstr(y, 0, indicator)
                    stdscr.addstr(id_str, curses.color_pair(2))
                    stdscr.addstr(" ")
                    stdscr.addstr(desc, curses.color_pair(3))
                    stdscr.addstr(" ")
                    stdscr.addstr(command)
                    stdscr.addstr(" ")
                    stdscr.addstr(tags, curses.color_pair(4))
            except curses.error:
                pass
        
        # ═══════════════════════════════════════════════════════════════
        # Preview Box
        # ═══════════════════════════════════════════════════════════════
        preview_y = height - preview_height - 1
        
        try:
            stdscr.addstr(preview_y, 0, "─" * (width - 1), curses.A_DIM)
            
            current_cmd = commands[current_idx]
            
            # Command preview
            stdscr.addstr(preview_y + 1, 0, " CMD: ", curses.color_pair(7) | curses.A_BOLD)
            full_cmd = current_cmd.get('command', '')[:width - 8]
            stdscr.addstr(full_cmd)
            
            # Description
            desc = current_cmd.get('description', '') or "(no description)"
            stdscr.addstr(preview_y + 2, 0, " DESC: ", curses.A_DIM)
            stdscr.addstr(desc[:width - 8])
            
            # Tags
            tags = ', '.join(current_cmd.get('tags', [])) or "(no tags)"
            stdscr.addstr(preview_y + 3, 0, " TAGS: ", curses.color_pair(4))
            stdscr.addstr(tags[:width - 8])
            
        except curses.error:
            pass
        
        # ═══════════════════════════════════════════════════════════════
        # Footer
        # ═══════════════════════════════════════════════════════════════
        try:
            footer = f" {current_idx + 1}/{len(commands)} │ ↑↓:Move  Enter:RUN  q:Quit "
            stdscr.addstr(height - 1, 0, footer[:width-1].ljust(width-1), curses.color_pair(6) | curses.A_BOLD)
        except curses.error:
            pass
        
        stdscr.refresh()
        
        # ═══════════════════════════════════════════════════════════════
        # Handle Input
        # ═══════════════════════════════════════════════════════════════
        key = stdscr.getch()
        
        if key == curses.KEY_UP or key == ord('k'):
            current_idx = max(0, current_idx - 1)
        elif key == curses.KEY_DOWN or key == ord('j'):
            current_idx = min(len(commands) - 1, current_idx + 1)
        elif key == curses.KEY_PPAGE:
            current_idx = max(0, current_idx - list_height)
        elif key == curses.KEY_NPAGE:
            current_idx = min(len(commands) - 1, current_idx + list_height)
        elif key == curses.KEY_HOME:
            current_idx = 0
        elif key == curses.KEY_END:
            current_idx = len(commands) - 1
        elif key in [ord('\n'), curses.KEY_ENTER, 10, 13]:
            return commands[current_idx]['id']
        elif key == ord('q') or key == 27:
            return None
