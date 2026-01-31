"""Command-line interface handler."""

import sys
from typing import List, Optional
from .manager import CommandManager
from .executor import CommandExecutor
from .printer import CommandPrinter
from .variables import find_placeholders, substitute_positional, prompt_for_values, substitute
from .tui import interactive_select
from .importer import get_history_file, read_history, filter_trivial
from pathlib import Path

class CLI:
    """Command-line interface handler."""
    
    def __init__(self, manager: CommandManager, executor: CommandExecutor, printer: CommandPrinter):
        self.manager = manager
        self.executor = executor
        self.printer = printer
    
    def handle_add(self, description: str, tags: List[str], command: str, 
                   save_only: bool = False, silent: bool = False, shell_mode: bool = False):
        """Handle adding and optionally executing a command."""
        cmd = self.manager.add(command, description, tags)
        
        if not silent:
            if cmd.get('updated'):
                action = "Merged tags for" if cmd.get('merged_tags') else "Already exists:"
                print(f"ℹ {action} command ID: {cmd['id']}", file=sys.stderr)
            else:
                print(f"✓ Command saved with ID: {cmd['id']}", file=sys.stderr)
        
        # Execute unless --save-only flag is set
        if not save_only:
            if shell_mode:
                # Just print the command for shell evaluation
                print(command)
            else:
                if not silent:
                    print(f"\n Running: {description}", file=sys.stderr)
                    print(f"   Command: {command}\n", file=sys.stderr)
                
                success, code = self.executor.execute(command)
                
                if not silent:
                    if success:
                        print(f"\n Command completed successfully", file=sys.stderr)
                    else:
                        print(f"\n Command exited with code {code}", file=sys.stderr)
    
    def handle_run(self, cmd_id: int, dry_run: bool = False, 
                   silent: bool = False, shell_mode: bool = False,
                   args: Optional[List[str]] = None):
        """Handle running a saved command."""        
        cmd = self.manager.get(cmd_id)
        if not cmd:
            print(f"✗ Command {cmd_id} not found.", file=sys.stderr)
            return False
        
        command = cmd['command']
        
        # Handle placeholders
        placeholders = find_placeholders(command)
        if placeholders:
            if args:
                # Use positional args
                command = substitute_positional(command, args)
            else:
                # Prompt for values
                print(f"Command has placeholders: {', '.join(placeholders)}", file=sys.stderr)
                values = prompt_for_values(placeholders)
                if not values:
                    print("Cancelled.", file=sys.stderr)
                    return False
                command = substitute(command, values)
        
        if shell_mode:
            # Print command for shell wrapper to evaluate
            print(command)
            self.manager.increment_usage(cmd_id)
            return True
        
        if dry_run:
            if not silent:
                print(f"(Dry run) Would execute: {command}", file=sys.stderr)
            return True
        
        success, code = self.executor.execute(command)
        
        if success:
            self.manager.increment_usage(cmd_id)
        return success
    
    def handle_search(self, query: Optional[str] = None, tags: Optional[List[str]] = None):
        """Handle searching commands."""
        results = self.manager.search(query=query, tags=tags)
        if results:
            for cmd in results:
                self.printer.print_command(cmd)
        else:
            print("No commands found matching your search.")
    
    def handle_list(self, tags: Optional[List[str]] = None, limit: Optional[int] = None, sort: str = 'created'):
        """Handle listing commands."""
        commands = self.manager.search(tags=tags)
        
        if not commands:
            print("No commands found.")
            return
        
        # Apply sorting
        if sort == 'recent':
            commands = sorted(commands, key=lambda x: x.get('last_used_at', ''), reverse=True)
        elif sort == 'used':
            commands = sorted(commands, key=lambda x: x.get('used_count', 0), reverse=True)
        else:  # created (default)
            commands = sorted(commands, key=lambda x: x.get('created_at', ''), reverse=True)
        
        if limit:
            commands = commands[:limit]
        
        self.printer.print_table(commands)
    
    def handle_show(self, cmd_id: int, copy_to_clipboard: bool = False):
        """Handle showing a specific command."""
        cmd = self.manager.get(cmd_id)
        if cmd:
            self.printer.print_command(cmd)
            self.manager.increment_usage(cmd_id)
            if copy_to_clipboard:
                from clipboard import copy
                success, message = copy(cmd['command'])
                if success:
                    print(f"\n {message}")
                else:
                    print(f"\n {message}")
        else:
            print(f"Command {cmd_id} not found.")
    
    def handle_delete(self, cmd_ids: List[int]):
        """Handle deleting one or more commands."""
        # Ensure cmd_ids is a list (in case it's passed as single int)
        if isinstance(cmd_ids, int):
            cmd_ids = [cmd_ids]
            
        count = self.manager.delete_multiple(cmd_ids)
        if count > 0:
            if count == 1:
                print(f" Command deleted.")
            else:
                print(f" {count} commands deleted.")
        else:
            print(f" No commands found to delete.")

    def handle_edit(self, cmd_id: int, description: Optional[str] = None, tags: Optional[List[str]] = None):
        """Handle editing a command."""
        cmd = self.manager.edit(cmd_id, description, tags)
        if cmd:
            print(f"Command {cmd_id} updated.")
            self.printer.print_command(cmd)
        else:
            print(f"Command {cmd_id} not found.")
    
    def handle_stats(self):
        """Handle showing statistics."""
        stats = self.manager.get_stats()
        self.printer.print_stats(stats)

    def handle_tags(self):
        """Handle listing all tags with counts."""
        tag_counts = self.manager.get_all_tags()
        if not tag_counts:
            print("No tags found.")
            return
        
        # Sort by count (descending), then alphabetically
        sorted_tags = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))
        
        print("\nTags:")
        print("-" * 30)
        for tag, count in sorted_tags:
            print(f"  {tag} ({count})")

    def handle_interactive(self, shell_mode: bool = False):
        """Handle interactive command selection."""
        
        commands = self.manager.search()  # Get all commands
        if not commands:
            print("No commands found.")
            return
        
        # Sort by most recently used
        commands = sorted(commands, key=lambda x: x.get('last_used_at', ''), reverse=True)
        
        selected_id = interactive_select(commands)
        if selected_id is not None:
            # Always execute directly (not shell_mode) since curses interferes with shell capture
            self.handle_run(selected_id, shell_mode=False)

    def handle_import(self, from_history: bool = False, lines: int = 50, 
                     file_path: Optional[str] = None, no_filter: bool = False):
        """Handle importing commands from history or file."""        
        # Determine source
        if file_path:
            source = Path(file_path)
            if not source.exists():
                print(f"File not found: {file_path}")
                return
        elif from_history:
            source = get_history_file()
            if not source:
                print("Could not find shell history file.")
                return
            print(f"Reading from: {source}")
        else:
            print("Please specify --history or --file")
            return
        
        # Read commands
        commands = read_history(source, lines)
        if not commands:
            print("No commands found in history.")
            return
        
        # Filter trivial commands
        if not no_filter:
            commands = filter_trivial(commands)
        
        if not commands:
            print("No interesting commands found after filtering.")
            return
        
        print(f"\nFound {len(commands)} commands to import:")
        print("-" * 40)
        
        imported = 0
        skipped = 0
        
        for cmd in commands:
            # Print first 60 chars of command
            display = cmd[:60] + "..." if len(cmd) > 60 else cmd
            
            # Try to add (will dedupe automatically)
            result = self.manager.add(cmd, "", [])
            
            if result.get('updated', True):  # Already existed
                skipped += 1
                print(f"  SKIP: {display}")
            else:
                imported += 1
                print(f"  ADD:  {display}")
        
        print("-" * 40)
        print(f"Imported: {imported}, Skipped (exists): {skipped}")
