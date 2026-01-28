"""Command-line interface handler."""

import sys
from typing import List, Optional
from manager import CommandManager
from executor import CommandExecutor
from printer import CommandPrinter


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
            print(f" Command saved with ID: {cmd['id']}", file=sys.stderr)
        
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
                   silent: bool = False, shell_mode: bool = False):
        """Handle running a saved command."""
        cmd = self.manager.get(cmd_id)
        if not cmd:
            print(f"✗ Command {cmd_id} not found.", file=sys.stderr)
            return False
        
        if shell_mode:
            # Print command for shell wrapper to evaluate
            print(cmd['command'])
            self.manager.increment_usage(cmd_id)
            return True
        
        if not silent:
            print(f"\n Running: {cmd['description']}", file=sys.stderr)
            print(f"   Command: {cmd['command']}\n", file=sys.stderr)
        
        if dry_run:
            if not silent:
                print("(Dry run - command not executed)", file=sys.stderr)
            return True
        
        success, code = self.executor.execute(cmd['command'])
        
        if success:
            self.manager.increment_usage(cmd_id)
        
        if not silent:
            if success:
                print(f"\n Command completed successfully", file=sys.stderr)
            else:
                print(f"\n Command exited with code {code}", file=sys.stderr)
        
        return success
    
    def handle_search(self, query: Optional[str] = None, tags: Optional[List[str]] = None):
        """Handle searching commands."""
        results = self.manager.search(query=query, tags=tags)
        if results:
            for cmd in results:
                self.printer.print_command(cmd)
        else:
            print("No commands found matching your search.")
    
    def handle_list(self, tags: Optional[List[str]] = None, limit: Optional[int] = None):
        """Handle listing commands."""
        commands = self.manager.search(tags=tags)
        
        if not commands:
            print("No commands found.")
            return
        
        # Sort by most recently created
        commands = sorted(commands, key=lambda x: x.get('created_at', ''), reverse=True)
        
        if limit:
            commands = commands[:limit]
        
        for cmd in commands:
            self.printer.print_command(cmd)
    
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
    
    def handle_delete(self, cmd_id: int):
        """Handle deleting a command."""
        if self.manager.delete(cmd_id):
            print(f" Command {cmd_id} deleted.")
        else:
            print(f" Command {cmd_id} not found.")
    
    def handle_stats(self):
        """Handle showing statistics."""
        stats = self.manager.get_stats()
        self.printer.print_stats(stats)
