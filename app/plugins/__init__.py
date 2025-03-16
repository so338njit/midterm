"""Plugins package initialization."""
from app.plugins.plugin_interface import PluginInterface
from app.plugins.plugin_manager import PluginManager

# Create a singleton instance of the plugin manager
_plugin_manager = PluginManager()

# Function to get the plugin manager instance
def get_plugin_manager() -> PluginManager:
    """Return the singleton plugin manager instance."""
    return _plugin_manager
