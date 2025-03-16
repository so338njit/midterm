"""Calculator module providing basic arithmetic operations using plugins.

This module implements a Calculator class that uses plugins to perform
various operations while maintaining a history of calculations.
"""
# pylint - disable=unused-import
from decimal import Decimal
from typing import Dict, Type, Any

from app.commands import CommandHandler
from app.commands.command import Command
from app.plugins import get_plugin_manager
from app.config import DECIMAL_PRECISION


class Calculator:
    """A calculator class that performs operations using the plugin system."""

    def __init__(self):
        """Initialize calculator with a command handler and load plugins."""
        self.command_handler = CommandHandler()

        # Get the plugin manager and discover operation plugins
        self.plugin_manager = get_plugin_manager()
        self.plugin_manager.discover_plugins("app.plugins.operations")

        # Cache available operations for faster lookup
        self._operations = self.plugin_manager.get_plugins("operation")

        # Initialize method cache
        self._method_cache = {}

        # Dynamically create methods for each operation
        self._create_operation_methods()

    def _create_operation_methods(self):
        """Dynamically create methods for each available operation."""
        for plugin_name, plugin_class in self._operations.items():
            if plugin_name not in self._method_cache:
                # Create a bound method for this operation
                method = self._create_operation_method(plugin_class)
                
                # Add the method to the cache and set it as an attribute
                self._method_cache[plugin_name] = method
                setattr(self, plugin_name, method)

    def _create_operation_method(self, plugin_class):
        """
        Create a method that uses the given plugin class.

        Args:
            plugin_class: The plugin class to create a method for

        Returns:
            A bound method that can be called on the calculator
        """
        command_class = plugin_class.get_command_class()
        
        def operation_method(self, a: Decimal, b: Decimal) -> Decimal:
            """
            Perform the operation on two numbers.

            Args:
                a: First operand
                b: Second operand

            Returns:
                The result of the operation
            """
            command = command_class(a, b)
            return self.command_handler.execute(command)

        # Set the method's docstring and name
        operation_method.__doc__ = f"Perform the {plugin_class.get_name()} operation."
        operation_method.__name__ = plugin_class.get_name()

        # Create a bound method
        from types import MethodType
        return MethodType(operation_method, self)

    def get_available_operations(self) -> Dict[str, str]:
        """Get a dictionary of available operations."""
        return {name: plugin.get_plugin_type() for name, plugin in self._operations.items()}

    def get_history(self):
        """Return the calculation history."""
        return self.command_handler.get_history()

    def reload_plugins(self):
        """Reload all plugins and update available operations."""
        self.plugin_manager.discover_plugins("app.plugins.operations")
        self._operations = self.plugin_manager.get_plugins("operation")
        self._create_operation_methods()
