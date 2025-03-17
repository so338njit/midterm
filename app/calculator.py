"""Calculator module providing basic arithmetic operations using plugins.

This module implements a Calculator class that uses plugins to perform
various operations while maintaining a history of calculations in CSV format.
"""
import logging
import os
import pandas as pd
import datetime
from decimal import Decimal
from typing import Dict, Type, Any, Optional, List, Union

from app.commands import CommandHandler
from app.commands.command import Command
from app.plugins import get_plugin_manager
from app.config import DECIMAL_PRECISION, DATA_DIRECTORY, CSV_HISTORY_FILE


# Ensure data directory exists
os.makedirs(DATA_DIRECTORY, exist_ok=True)


class Calculator:
    """A calculator class that performs operations using the plugin system."""

    def __init__(self, history_file: str = None):
        """Initialize calculator with a command handler and load plugins."""
        self.logger = logging.getLogger(__name__)
        self.command_handler = CommandHandler()
        self.history_file = history_file or CSV_HISTORY_FILE

        # Ensure the history file directory exists
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

        if not os.path.exists(self.history_file):
            empty_df = pd.DataFrame(columns=['timestamp', 'operation', 'a', 'b', 'result'])
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            empty_df.to_csv(self.history_file, index=False)
            self.logger.info(f"Created empty history file at {self.history_file}")

        # Get the plugin manager and discover operation plugins
        self.plugin_manager = get_plugin_manager()
        self.plugin_manager.discover_plugins("app.plugins.operations")

        # Also discover history plugins
        self.plugin_manager.discover_plugins("app.plugins.history")

        # Cache available operations for faster lookup
        self._operations = self.plugin_manager.get_plugins("operation")

        # Initialize history data
        self._history_data = self._load_history()

        # Initialize method cache
        self._method_cache = {}

        # Dynamically create methods for each operation
        self._create_operation_methods()

    def _load_history(self) -> pd.DataFrame:
        """Load history data using the load_history plugin."""
        load_plugin = self.plugin_manager.get_plugin('history', 'load_history')
        if not load_plugin:
            self.logger.warning("Load history plugin not found")
            return pd.DataFrame(columns=['timestamp', 'operation', 'a', 'b', 'result'])

        command_class = load_plugin.get_command_class()
        command = command_class(kwargs={'file_path': self.history_file})

        try:
            result = command.execute()
            # Ensure we have a DataFrame
            if not isinstance(result, pd.DataFrame):
                self.logger.warning("Load plugin did not return a DataFrame")
                return pd.DataFrame(columns=['timestamp', 'operation', 'a', 'b', 'result'])
            return result
        except Exception as e:
            self.logger.error("Failed to load history: %s", str(e))
            return pd.DataFrame(columns=['timestamp', 'operation', 'a', 'b', 'result'])

    def _save_history(self) -> None:
        """Save history data using the save_history plugin."""
        save_plugin = self.plugin_manager.get_plugin('history', 'save_history')
        if not save_plugin:
            self.logger.warning("Save history plugin not found")
            return

        # Make sure we have a proper DataFrame before saving
        if not isinstance(self._history_data, pd.DataFrame):
            self.logger.warning("History data is not a DataFrame, initializing empty DataFrame")
            self._history_data = pd.DataFrame(columns=['timestamp', 'operation', 'a', 'b', 'result'])

        command_class = save_plugin.get_command_class()
        command = command_class(kwargs={'file_path': self.history_file, 'history_data': self._history_data})

        try:
            command.execute()
            self.logger.debug("History saved to %s", self.history_file)
        except Exception as e:
            self.logger.error("Failed to save history: %s", str(e))

    def _add_to_history(self, operation: str, a: Decimal, b: Decimal, result: Decimal) -> None:
        """Add an operation to the history."""
        new_record = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation': operation,
            'a': float(a),  # Convert to float for better compatibility with pandas
            'b': float(b),
            'result': float(result)
        }

        self._history_data = pd.concat([self._history_data, pd.DataFrame([new_record])], ignore_index=True)
        self._save_history()

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
        operation_name = plugin_class.get_name()

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
            result = self.command_handler.execute(command)

            # Add to history
            self._add_to_history(operation_name, a, b, result)

            return result

        # Set the method's docstring and name
        operation_method.__doc__ = f"Perform the {plugin_class.get_name()} operation."
        operation_method.__name__ = plugin_class.get_name()

        # Create a bound method
        from types import MethodType
        return MethodType(operation_method, self)

    def get_available_operations(self) -> Dict[str, str]:
        """Get a dictionary of available operations."""
        return {name: plugin.get_plugin_type() for name, plugin in self._operations.items()}

    def get_history(self) -> pd.DataFrame:
        """Return the calculation history as a DataFrame."""
        return self._history_data.copy()

    def get_history_list(self) -> List[str]:
        """Return the calculation history as a formatted list of strings."""
        if len(self._history_data) == 0:
            return []

        history_list = []
        for idx, row in self._history_data.iterrows():
            operation = row['operation']
            a = row['a']
            b = row['b']
            result = row['result']

            if operation == 'add':
                history_list.append(f"{a} + {b} = {result}")
            elif operation == 'subtract':
                history_list.append(f"{a} - {b} = {result}")
            elif operation == 'multiply':
                history_list.append(f"{a} * {b} = {result}")
            elif operation == 'divide':
                history_list.append(f"{a} / {b} = {result}")
            else:
                history_list.append(f"{operation}({a}, {b}) = {result}")

        return history_list

    def get_pandas_history(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get the calculation history as a pandas DataFrame with optional limit.

        Args:
            limit: Optional limit on the number of records to return (most recent)

        Returns:
            DataFrame containing the history records
        """
        if limit is None or limit >= len(self._history_data):
            return self._history_data.copy()

        # Return only the most recent records
        start_idx = max(0, len(self._history_data) - limit)
        return self._history_data.iloc[start_idx:].copy().reset_index(drop=True)

    def clear_history(self) -> None:
        """Clear history."""        
        # Clear pandas history using plugin
        clear_plugin = self.plugin_manager.get_plugin('history', 'clear_history')
        if not clear_plugin:
            self.logger.warning("Clear history plugin not found")
            self._history_data = pd.DataFrame(columns=['timestamp', 'operation', 'a', 'b', 'result'])
            self._save_history()
            return

        command_class = clear_plugin.get_command_class()
        command = command_class()

        try:
            self._history_data = command.execute()
            self._save_history()
            self.logger.debug("History cleared")
        except Exception as e:
            self.logger.error("Failed to clear history: %s", str(e))

    def delete_history_record(self, index: int) -> None:
        """Delete a specific record from history."""
        if index < 0 or index >= len(self._history_data):
            self.logger.error("Index out of range: %s", index)
            raise ValueError(f"Index out of range: {index}")

        delete_plugin = self.plugin_manager.get_plugin('history', 'delete_history_record')
        if not delete_plugin:
            self.logger.warning("Delete history record plugin not found")
            # Fallback to manual deletion
            self._history_data = self._history_data.drop(index).reset_index(drop=True)
            self._save_history()
            return

        command_class = delete_plugin.get_command_class()
        command = command_class(kwargs={'history_data': self._history_data, 'index': index})

        try:
            self._history_data = command.execute()
            self._save_history()
            self.logger.debug("Record at index %d deleted", index)
        except Exception as e:
            self.logger.error("Failed to delete record: %s", str(e))
            raise

    def reload_plugins(self):
        """Reload all plugins and update available operations."""
        self.plugin_manager.discover_plugins("app.plugins.operations")
        self.plugin_manager.discover_plugins("app.plugins.history")
        self._operations = self.plugin_manager.get_plugins("operation")
        self._create_operation_methods()
