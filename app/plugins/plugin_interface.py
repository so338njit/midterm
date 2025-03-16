"""Plugin interface for calculator operations."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Type


class PluginInterface(ABC):
    """Base interface that all plugins must implement."""

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Return the name of the plugin."""
        pass

    @classmethod
    @abstractmethod
    def get_plugin_type(cls) -> str:
        """Return the type of the plugin (e.g., 'operation')."""
        pass

    @classmethod
    @abstractmethod
    def get_command_class(cls) -> Type:
        """Return the command class associated with this plugin."""
        pass
