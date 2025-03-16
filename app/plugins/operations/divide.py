"""Division operation plugin."""
import logging
from decimal import Decimal
from typing import Type

from app.commands.command import Command
from app.plugins.plugin_interface import PluginInterface
from app.config import DECIMAL_PRECISION

class DivideCommand(Command):
    """Command for division operation."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return "divide"

    def execute(self) -> Decimal:
        """Perform division."""
        logger = logging.getLogger(__name__)
        logger.debug("Dividing %s by %s", self.a, self.b)
        
        if self.b == 0:
            logger.warning("Division by zero attempted: %s / %s", self.a, self.b)
            raise ValueError("Division by zero is not allowed")
            
        result = self.a / self.b
        logger.debug("Division result: %s (using precision: %s)", result, DECIMAL_PRECISION)
        return result

    def __repr__(self):
        """String representation."""
        return f"DivideCommand({self.a}, {self.b})"


class DividePlugin(PluginInterface):
    """Plugin for division operation."""

    @classmethod
    def get_name(cls) -> str:
        """Return the name of the plugin."""
        return "divide"

    @classmethod
    def get_plugin_type(cls) -> str:
        """Return the type of the plugin."""
        return "operation"

    @classmethod
    def get_command_class(cls) -> Type[Command]:
        """Return the command class for this operation."""
        return DivideCommand
