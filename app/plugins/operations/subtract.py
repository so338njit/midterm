"""Subtraction operation plugin."""
import logging
from decimal import Decimal
from typing import Type

from app.commands.command import Command
from app.plugins.plugin_interface import PluginInterface


class SubtractCommand(Command):
    """Command for subtraction operation."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return "subtract"

    def execute(self) -> Decimal:
        """Perform subtraction."""
        logger = logging.getLogger(__name__)
        logger.debug("Subtracting %s from %s", self.b, self.a)
        
        result = self.a - self.b
        logger.debug("Subtraction result: %s", result)
        return result

    def __repr__(self):
        """String representation."""
        return f"SubtractCommand({self.a}, {self.b})"


class SubtractPlugin(PluginInterface):
    """Plugin for subtraction operation."""

    @classmethod
    def get_name(cls) -> str:
        """Return the name of the plugin."""
        return "subtract"

    @classmethod
    def get_plugin_type(cls) -> str:
        """Return the type of the plugin."""
        return "operation"

    @classmethod
    def get_command_class(cls) -> Type[Command]:
        """Return the command class for this operation."""
        return SubtractCommand
