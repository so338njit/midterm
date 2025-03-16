"""Plugin manager for discovering and loading calculator plugins."""
import importlib
import inspect
import os
import pkgutil
from typing import Dict, List, Type

from app.plugins.plugin_interface import PluginInterface


class PluginManager:
    """Discovers, loads, and manages plugins for the calculator."""

    def __init__(self):
        """Initialize the plugin manager with empty plugin registries."""
        self._plugins: Dict[str, Dict[str, Type[PluginInterface]]] = {}

    def discover_plugins(self, package_name: str) -> None:
        """
        Discover all plugins in the specified package.

        Args:
            package_name: The package to search for plugins (e.g., 'calculator.plugins.operations')
        """
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            print(f"Could not import {package_name}")
            return

        # Find all modules in the package
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
            if is_pkg:
                # Recursively discover plugins in subpackages
                self.discover_plugins(name)
            else:
                # Import the module and look for plugin classes
                try:
                    module = importlib.import_module(name)
                    self._register_plugins_from_module(module)
                except ImportError:
                    print(f"Could not import {name}")

    def _register_plugins_from_module(self, module) -> None:
        """
        Register plugins from a module.

        Args:
            module: The module to search for plugins
        """
        for _, obj in inspect.getmembers(module, inspect.isclass):
            # Check if it's a plugin (implements the interface and is not the interface itself)
            if (issubclass(obj, PluginInterface) and 
                obj is not PluginInterface and 
                not inspect.isabstract(obj)):

                plugin_type = obj.get_plugin_type()
                plugin_name = obj.get_name()

                # Initialize the plugin type registry if needed
                if plugin_type not in self._plugins:
                    self._plugins[plugin_type] = {}

                # Register the plugin
                self._plugins[plugin_type][plugin_name] = obj

    def get_plugins(self, plugin_type: str = None) -> Dict[str, Type[PluginInterface]]:
        """
        Get all plugins of a specific type.
        
        Args:
            plugin_type: The type of plugins to return, or None for all plugins
            
        Returns:
            A dictionary of plugin names to plugin classes
        """
        if plugin_type is None:
            # Return a flattened dictionary of all plugins
            result = {}
            for type_dict in self._plugins.values():
                result.update(type_dict)
            return result

        # Return plugins of the specified type
        return self._plugins.get(plugin_type, {})

    def get_plugin(self, plugin_type: str, plugin_name: str) -> Type[PluginInterface]:
        """
        Get a specific plugin.

        Args:
            plugin_type: The type of the plugin
            plugin_name: The name of the plugin

        Returns:
            The plugin class or None if not found
        """
        return self._plugins.get(plugin_type, {}).get(plugin_name)
