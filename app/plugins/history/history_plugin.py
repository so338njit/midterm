"""History management plugin using pandas."""
import logging
import os
import pandas as pd
from decimal import Decimal
from typing import Type, List, Dict, Any, Optional

from app.commands.command import Command
from app.plugins.plugin_interface import PluginInterface
from app.config import DATA_DIRECTORY, CSV_HISTORY_FILE


class HistoryCommand(Command):
    """Base command for history operations."""

    def __init__(self, a: Decimal = Decimal('0'), b: Decimal = Decimal('0'), **kwargs):
        """Initialize with optional parameters for history operations."""
        super().__init__(a, b)
        self.kwargs = kwargs
        self.logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        """Name of the command."""
        return "history"


class LoadHistoryCommand(HistoryCommand):
    """Command for loading calculator history."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return "load_history"

    def execute(self) -> pd.DataFrame:
        """Load calculation history from a CSV file."""
        file_path = self.kwargs.get('file_path', CSV_HISTORY_FILE)
        
        self.logger.debug("Loading history from %s", file_path)
        
        if not os.path.exists(file_path):
            self.logger.warning("History file %s not found", file_path)
            return pd.DataFrame(columns=['timestamp', 'operation', 'a', 'b', 'result'])
        
        try:
            df = pd.read_csv(file_path)
            self.logger.debug("Loaded %d history records", len(df))
            return df
        except Exception as e:
            self.logger.error("Failed to load history: %s", str(e))
            raise


class SaveHistoryCommand(HistoryCommand):
    """Command for saving calculator history."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return "save_history"

    def execute(self) -> bool:
        """Save calculation history to a CSV file."""
        file_path = self.kwargs.get('file_path', CSV_HISTORY_FILE)
        history_data = self.kwargs.get('history_data')
        
        if history_data is None or not isinstance(history_data, pd.DataFrame):
            self.logger.error("Invalid history data provided")
            raise ValueError("History data must be a pandas DataFrame")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        self.logger.debug("Saving %d history records to %s", len(history_data), file_path)
        
        try:
            history_data.to_csv(file_path, index=False)
            self.logger.debug("History saved successfully")
            return True
        except Exception as e:
            self.logger.error("Failed to save history: %s", str(e))
            raise


class ClearHistoryCommand(HistoryCommand):
    """Command for clearing calculator history."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return "clear_history"

    def execute(self) -> pd.DataFrame:
        """Clear all calculation history."""
        self.logger.debug("Clearing history")
        return pd.DataFrame(columns=['timestamp', 'operation', 'a', 'b', 'result'])


class DeleteHistoryRecordCommand(HistoryCommand):
    """Command for deleting a specific history record."""

    @property
    def name(self) -> str:
        """Name of the command."""
        return "delete_history_record"

    def execute(self) -> pd.DataFrame:
        """Delete a specific record from calculation history."""
        history_data = self.kwargs.get('history_data')
        index = self.kwargs.get('index')

        if history_data is None or not isinstance(history_data, pd.DataFrame):
            self.logger.error("Invalid history data provided")
            raise ValueError("History data must be a pandas DataFrame")

        if index is None:
            self.logger.error("No index provided for deletion")
            raise ValueError("Index must be provided for deletion")

        try:
            index = int(index)
        except ValueError:
            self.logger.error("Invalid index: %s", index)
            raise ValueError(f"Invalid index: {index}")

        if index < 0 or index >= len(history_data):
            self.logger.error("Index out of range: %s", index)
            raise ValueError(f"Index out of range: {index}")

        self.logger.debug("Deleting history record at index %d", index)

        # Create a copy of the DataFrame and drop the specified index
        result = history_data.copy()
        result = result.drop(index)
        result = result.reset_index(drop=True)  # Reset the index after deletion

        self.logger.debug("Record deleted, %d records remaining", len(result))
        return result


class HistoryPlugin(PluginInterface):
    """Plugin for history management operations."""

    @classmethod
    def get_name(cls) -> str:
        """Return the name of the plugin."""
        return "history"

    @classmethod
    def get_plugin_type(cls) -> str:
        """Return the type of the plugin."""
        return "history"

    @classmethod
    def get_command_class(cls) -> Type[Command]:
        """Return the base command class for history operations."""
        return HistoryCommand


class LoadHistoryPlugin(PluginInterface):
    """Plugin for loading history."""

    @classmethod
    def get_name(cls) -> str:
        """Return the name of the plugin."""
        return "load_history"

    @classmethod
    def get_plugin_type(cls) -> str:
        """Return the type of the plugin."""
        return "history"

    @classmethod
    def get_command_class(cls) -> Type[Command]:
        """Return the command class for loading history."""
        return LoadHistoryCommand


class SaveHistoryPlugin(PluginInterface):
    """Plugin for saving history."""

    @classmethod
    def get_name(cls) -> str:
        """Return the name of the plugin."""
        return "save_history"

    @classmethod
    def get_plugin_type(cls) -> str:
        """Return the type of the plugin."""
        return "history"

    @classmethod
    def get_command_class(cls) -> Type[Command]:
        """Return the command class for saving history."""
        return SaveHistoryCommand


class ClearHistoryPlugin(PluginInterface):
    """Plugin for clearing history."""

    @classmethod
    def get_name(cls) -> str:
        """Return the name of the plugin."""
        return "clear_history"

    @classmethod
    def get_plugin_type(cls) -> str:
        """Return the type of the plugin."""
        return "history"

    @classmethod
    def get_command_class(cls) -> Type[Command]:
        """Return the command class for clearing history."""
        return ClearHistoryCommand


class DeleteHistoryRecordPlugin(PluginInterface):
    """Plugin for deleting a specific history record."""

    @classmethod
    def get_name(cls) -> str:
        """Return the name of the plugin."""
        return "delete_history_record"

    @classmethod
    def get_plugin_type(cls) -> str:
        """Return the type of the plugin."""
        return "history"

    @classmethod
    def get_command_class(cls) -> Type[Command]:
        """Return the command class for deleting a history record."""
        return DeleteHistoryRecordCommand
