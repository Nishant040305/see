"""Business logic for command management."""

from typing import List, Dict, Optional
from datetime import datetime
from storage import CommandStorage


class CommandManager:
    """Manages command operations."""
    
    def __init__(self, storage: CommandStorage):
        self.storage = storage
        self.commands = self.storage.load()
    
    def add(self, command: str, description: str, tags: List[str]) -> Dict:
        """Add a new command to the collection."""
        new_command = {
            'id': self._get_next_id(),
            'command': command,
            'description': description,
            'tags': tags,
            'created_at': datetime.now().isoformat(),
            'used_count': 0
        }
        self.commands.append(new_command)
        self.storage.save(self.commands)
        return new_command
    
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
        """Delete a command by ID. Returns True if deleted."""
        original_length = len(self.commands)
        self.commands = [cmd for cmd in self.commands if cmd['id'] != cmd_id]
        
        if len(self.commands) < original_length:
            self.storage.save(self.commands)
            return True
        return False
    
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
        """Increment the usage count for a command."""
        cmd = self.get(cmd_id)
        if cmd:
            cmd['used_count'] = cmd.get('used_count', 0) + 1
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
