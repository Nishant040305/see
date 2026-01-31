"""Business logic for command management."""

from typing import List, Dict, Optional
from datetime import datetime
from .storage import CommandStorage


class CommandManager:
    """Manages command operations."""
    
    def __init__(self, storage: CommandStorage):
        self.storage = storage
        self.commands = self.storage.load()
    
    def add(self, command: str, description: str, tags: List[str], **kwargs) -> Dict:
        """Add a new command to the collection or update existing if found."""
        command = command.strip()
        
        alias = kwargs.get('alias')
        
        # Check alias uniqueness (initial check, detailed check in validate_alias)
        if alias:
            # We defer full validation to just before saving for new commands, 
            # or we can check here. Let's check here to fail early.
            # However, for 'add', we don't have an ID yet for the new command.
            # So pass None for current_cmd_id.
            # But wait, we might return an existing command.
            pass # Validation happens inside validate_alias logic handling


        # Check for existing command
        existing = self._find_by_command(command)
        if existing:
            # Update alias if provided
            updated = False
            if alias and existing.get('alias') != alias:
                existing['alias'] = alias
                updated = True

            # Merge tags
            existing_tags = set(existing['tags'])
            new_tags = set(tags)
            if not new_tags.issubset(existing_tags):
                existing['tags'] = sorted(list(existing_tags.union(new_tags)))
                updated = True
                merged_tags = True
            else:
                merged_tags = False
            
            if updated:
                self.storage.save(self.commands)
            
            return {**existing, 'updated': updated, 'merged_tags': merged_tags}

        new_command = {
            'id': self._get_next_id(),
            'command': command,
            'description': description,
            'tags': tags,
            'alias': kwargs.get('alias'),  # Add alias support
            'created_at': datetime.now().isoformat(),
            'used_count': 0
        }
        
        # Validate alias if provided
        if new_command['alias']:
            self.validate_alias(new_command['alias'], new_command['id'])

        self.commands.append(new_command)
        self.storage.save(self.commands)
        return new_command

    def validate_alias(self, alias: str, current_cmd_id: Optional[int] = None):
        """Validate that an alias is not a reserved keyword and is unique."""
        if not alias:
            return

        if alias.startswith('-'):
            raise ValueError(f"Alias '{alias}' cannot start with '-'.")

        # Check reserved keywords
        RESERVED_KEYWORDS = {
            # See subcommands and common args
            'search', 'list', 'show', 'run', 'delete', 'edit', 'stats', 
            'install', 'import', 'tags', 'interactive', 'i', 'alias', 'help',
            'see', 'add', # 'add' is implicit default, 'see' prevents recursion
            
            # Shell builtins and common commands
            'cd', 'exit', 'logout', 'pwd', 'clear', 'history', 'type', 
            'alias', 'unalias', 'export', 'unset', 'set', 'env', 
            'source', '.', 'ls', 'cp', 'mv', 'rm', 'mkdir', 'grep',
            'cat', 'echo', 'man', 'sudo', 'which', 'whoami',
            'true', 'false', 'test'
        }
        
        if alias in RESERVED_KEYWORDS:
            raise ValueError(f"Alias '{alias}' is a reserved keyword.")

        # Check uniqueness
        existing = self.get_by_alias(alias)
        if existing and (current_cmd_id is None or existing['id'] != current_cmd_id):
            raise ValueError(f"Alias '{alias}' is already in use by ID {existing['id']}")


    def get_by_alias(self, alias: str) -> Optional[Dict]:
        """Find a command by its alias."""
        if not alias:
            return None
        for cmd in self.commands:
            if cmd.get('alias') == alias:
                return cmd
        return None

    def edit(self, cmd_id: int, description: Optional[str] = None, 
             tags: Optional[List[str]] = None, alias: Optional[str] = None) -> Optional[Dict]:

        """Edit an existing command."""
        cmd = self.get(cmd_id)
        if not cmd:
            return None
        
        updated = False
        if description:
            cmd['description'] = description
            updated = True
            
        if tags is not None:
            # For edit, we replace tags
            cmd['tags'] = tags
            updated = True
        
        if alias is not None:
            if alias != cmd.get('alias'):
                # Validate new alias
                self.validate_alias(alias, cmd_id)
                cmd['alias'] = alias
                updated = True
            
        if updated:
            self.storage.save(self.commands)
            
        return cmd

    def _find_by_command(self, command_str: str) -> Optional[Dict]:
        """Find a command by its command string."""
        for cmd in self.commands:
            if cmd['command'].strip() == command_str:
                return cmd
        return None
    
    def _get_next_id(self) -> int:
        """Get the next available ID."""
        if not self.commands:
            return 1
        return max(cmd['id'] for cmd in self.commands) + 1
    
    def get(self, cmd_id: int) -> Optional[Dict]:
        """Get a specific command by ID."""
        for cmd in self.commands:
            if cmd['id'] == cmd_id:
                return cmd
        return None
    
    def delete(self, cmd_id: int) -> bool:
        """Delete a single command by ID. Returns True if deleted."""
        return self.delete_multiple([cmd_id]) > 0

    def delete_multiple(self, cmd_ids: List[int]) -> int:
        """Delete multiple commands by ID. Returns number of deleted commands."""
        original_length = len(self.commands)
        target_ids = set(cmd_ids)
        self.commands = [cmd for cmd in self.commands if cmd['id'] not in target_ids]
        
        deleted_count = original_length - len(self.commands)
        if deleted_count > 0:
            self.storage.save(self.commands)
            
        return deleted_count
    
    def search(self, query: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict]:
        """Search commands by query string or tags."""
        results = self.commands
        
        if tags:
            results = [
                cmd for cmd in results
                if any(tag.lower() in [t.lower() for t in cmd['tags']] for tag in tags)
            ]
        
        if query:
            query_lower = query.lower()
            results = [
                cmd for cmd in results
                if query_lower in cmd['command'].lower() or
                   query_lower in cmd['description'].lower()
            ]
        
        return results
    
    def increment_usage(self, cmd_id: int):
        """Increment the usage count and update last_used_at for a command."""
        cmd = self.get(cmd_id)
        if cmd:
            cmd['used_count'] = cmd.get('used_count', 0) + 1
            cmd['last_used_at'] = datetime.now().isoformat()
            self.storage.save(self.commands)
    
    def get_stats(self) -> Dict:
        """Get statistics about saved commands."""
        all_tags = set()
        for cmd in self.commands:
            all_tags.update(cmd['tags'])
        
        most_used = sorted(
            self.commands,
            key=lambda x: x.get('used_count', 0),
            reverse=True
        )[:5]
        
        return {
            'total': len(self.commands),
            'unique_tags': len(all_tags),
            'tags': sorted(all_tags),
            'most_used': [cmd for cmd in most_used if cmd.get('used_count', 0) > 0]
        }

    def get_all_tags(self) -> Dict[str, int]:
        """Get all unique tags with their usage counts."""
        tag_counts = {}
        for cmd in self.commands:
            for tag in cmd.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return tag_counts
