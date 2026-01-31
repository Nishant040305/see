"""Argument parsing and command routing."""

import argparse
import shlex
import sys
from typing import List, Dict, Optional


def parse_add_syntax(args_list: List[str]) -> Optional[Dict]:
    """Parse the custom add syntax: see -d 'desc' -t tag1 tag2 -c <command>"""
    description = None
    tags = []
    alias = None
    save_only = False
    shell_mode = True  # Enable shell mode by default for quiet execution
    command_parts = []
    
    i = 0
    while i < len(args_list):
        arg = args_list[i]
        
        if arg in ['-d', '--description']:
            if i + 1 < len(args_list):
                description = args_list[i + 1]
                i += 2
            else:
                print("Error: -d requires a description", file=sys.stderr)
                return None
        elif arg in ['-t', '--tags']:
            # Collect tags until we hit another flag
            i += 1
            while i < len(args_list) and not args_list[i].startswith('-'):
                tags.append(args_list[i])
                i += 1
        elif arg in ['-c', '--command']:
            # Everything after -c is the command
            i += 1
            command_parts = args_list[i:]
            break
        elif arg in ['-s', '--save-only']:
            save_only = True
            i += 1
        elif arg in ['-a', '--alias']:
            if i + 1 < len(args_list):
                alias = args_list[i + 1]
                i += 2
            else:
                print("Error: -a requires an alias name", file=sys.stderr)
                return None
        elif arg in ['-v', '--verbose']:
            shell_mode = False  # Disable shell mode (show output)
            i += 1
        elif arg in ['-h', '--help']:
            return {'help': True}
        else:
            # If we encounter something that's not a flag and we haven't seen -c yet,
            # treat everything from here as the command
            command_parts = args_list[i:]
            break
    
    if description is not None:
        if not command_parts:
            print("Error: No command specified.", file=sys.stderr)
            print("Usage: see -d 'description' -t tag1 tag2 [-a alias] -c <command>", file=sys.stderr)
            return None
        
        return {
            'description': description,
            'tags': tags,
            'alias': locals().get('alias'),
            'command': shlex.join(command_parts),
            'save_only': save_only,
            'shell_mode': shell_mode
        }
    
    return None


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for subcommands."""
    parser = argparse.ArgumentParser(
        description='SEE - CLI Command Helper',
        add_help=False
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search commands')
    search_parser.add_argument('query', nargs='*', help='Search query')
    search_parser.add_argument('-t', '--tags', nargs='+', help='Filter by tags')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all commands')
    list_parser.add_argument('-t', '--tags', nargs='+', help='Filter by tags')
    list_parser.add_argument('-n', '--limit', type=int, help='Limit number of results')
    list_parser.add_argument('-s', '--sort', choices=['created', 'recent', 'used'], 
                            default='created', help='Sort order: created (newest first), recent (last used), used (most used)')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show a specific command by ID')
    show_parser.add_argument('id', type=int, help='Command ID')
    show_parser.add_argument('-c', '--copy', action='store_true', help='Copy command to clipboard')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Execute a saved command by ID')
    run_parser.add_argument('id', type=int, help='Command ID to execute')
    run_parser.add_argument('args', nargs='*', help='Values for {{placeholders}} in order')
    run_parser.add_argument('--dry-run', action='store_true', help='Show what would be executed without running')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Show execution details (disable shell integration)')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a command by ID')
    delete_parser.add_argument('id', type=int, nargs='+', help='Command ID(s) to delete')

    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit a command by ID')
    edit_parser.add_argument('id', type=int, help='Command ID to edit')
    edit_parser.add_argument('-d', '--description', help='New description')
    edit_parser.add_argument('-t', '--tags', nargs='+', help='New tags (replaces existing)')
    
    # Tags command
    tags_parser = subparsers.add_parser('tags', help='List all tags with counts')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', aliases=['i'], help='Interactive command selector')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import commands from history')
    import_parser.add_argument('--history', action='store_true', help='Import from shell history file')
    import_parser.add_argument('--lines', type=int, default=50, help='Number of history lines to scan (default: 50)')
    import_parser.add_argument('--file', type=str, help='Import from a specific file path')
    import_parser.add_argument('--no-filter', action='store_true', help='Skip filtering trivial commands')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install shell wrapper')
    install_parser.add_argument('shell', nargs='?', choices=['bash', 'zsh', 'fish'], 
                               help='Shell to install for (auto-detected if not specified)')
    
    # Alias command
    alias_parser = subparsers.add_parser('alias', help='Assign alias to a command')
    alias_parser.add_argument('id', type=int, help='Command ID')
    alias_parser.add_argument('-a', '--alias', required=True, help='Alias name')

    return parser


def print_help(file=sys.stdout):
    """Print help message."""
    help_text = """
SEE - CLI Command Helper: Save and search your CLI commands

Usage:
  # Add and execute a command (default)
  see -d "description" -t tag1 tag2 [-a alias] -c <command>
  
  # Add without executing
  see -s -d "description" -t tag1 tag2 [-a alias] -c <command>
  
  # Subcommands
  see search [query] [-t tag1 tag2]
  see list [-t tag1 tag2] [-n limit]
  see show <id>
  see show <id> -c #to copy to clipboard
  see run <id> [--dry-run]
  see edit <id> [-d description] [-t tags]
  see edit <id> [-d description] [-t tags]
  see delete <id>
  see stats
  see alias <id> -a <alias>
  see <alias>
  see install [bash|zsh|fish]

Examples:
  see -d "List files" -t files -c ls -lah
  see -d "Set proxy" -t proxy network -c export https_proxy=http://proxy:3128
  see -s -d "Docker cleanup" -t docker cleanup -c docker system prune -a
  
  see search docker
  see list -t git
  see run 3
  see alias 3 -a mycmd
  see mycmd
  see stats
  see install

Options:
  -d, --description    Description of the command (required for add)
  -t, --tags          Tags for categorization (space-separated)
  -a, --alias         Alias name (for 'add' or 'alias' subcommand)
  -c, --command       Marks the start of the command (everything after is the command)
  -s, --save-only     Save without executing (default is to execute)
  -v, --verbose       Show execution details (disable quiet shell mode)
  -h, --help          Show this help message

Note: The -c flag is optional but recommended for clarity. If omitted, everything
      after the flags will be treated as the command.

Shell Integration:
  Run 'see install' to set up shell integration. This allows commands like
  'export' to affect your current shell session.
"""
    print(help_text, file=file)
