"""Command handler that executes commands and maintains history"""
import logging
from typing import List
from app.commands.command import Command
from app.config import MAX_HISTORY_SIZE

class CommandHandler:
    """Handles the execution of commands and maintains history"""

    def __init__(self):
        """Initialize with empty history"""
        self.logger = logging.getLogger(__name__)
        self.history: List[Command] = []
        self.max_history_size = MAX_HISTORY_SIZE
        self.logger.debug("CommandHandler initialized with max_history_size=%d", self.max_history_size)

    def add_to_history(self, command):
        """Add a command to history with size limit enforcement"""
        self.history.append(command)
        
        if len(self.history) > self.max_history_size:
            removed_command = self.history[0]
            self.history = self.history[-self.max_history_size:]
            self.logger.debug(
                "History size exceeded limit (%d). Removed oldest command: %r", 
                self.max_history_size, 
                removed_command
            )
        
        self.logger.debug("Command added to history: %r", command)

    def execute(self, command: Command):
        """Execute a command and store it in history"""
        self.logger.info("Executing command: %r", command)
        
        try:
            result = command.execute()
            self.add_to_history(command)
            self.logger.debug("Command executed successfully, result: %s", result)
            return result
        except Exception as e:
            self.logger.error("Error executing command: %s", str(e))
            raise

    def get_history(self) -> List[Command]:
        """Return the command history"""
        self.logger.debug("Getting command history (size: %d)", len(self.history))
        return self.history

    def clear_history(self):
        """Clear the command history"""
        history_size = len(self.history)
        self.history.clear()
        self.logger.info("Command history cleared (removed %d commands)", history_size)

    def get_latest(self):
        """Get the most recent command"""
        if self.history:
            latest = self.history[-1]
            self.logger.debug("Getting latest command: %r", latest)
            return latest
        
        self.logger.debug("No commands in history")
        return None

    def find_by_command_name(self, name: str) -> List[Command]:
        """Find commands by name"""
        self.logger.debug("Finding commands with name: %s", name)
        matching_commands = [cmd for cmd in self.history if cmd.name == name]
        self.logger.debug("Found %d commands with name: %s", len(matching_commands), name)
        return matching_commands
