"""Multiplication operation plugin."""
import logging
from decimal import Decimal
from typing import Type

from app.commands.command import Command
from app.plugins.plugin_interface import PluginInterface


class MultiplyCommand(Command):
    """Command for multiplication operation."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return "multiply"

    def execute(self) -> Decimal:
        """Perform multiplication."""
        logger = logging.getLogger(__name__)
        logger.debug("Multiplying %s by %s", self.a, self.b)
        
        result = self.a * self.b
        logger.debug("Multiplication result: %s", result)
        return result

    def __repr__(self):
        """String representation."""
        return f"MultiplyCommand({self.a}, {self.b})"


class MultiplyPlugin(PluginInterface):
    """Plugin for multiplication operation."""

    @classmethod
    def get_name(cls) -> str:
        """Return the name of the plugin."""
        return "multiply"

    @classmethod
    def get_plugin_type(cls) -> str:
        """Return the type of the plugin."""
        return "operation"

    @classmethod
    def get_command_class(cls) -> Type[Command]:
        """Return the command class for this operation."""
        return MultiplyCommand
