# pylint: disable=unused-import, protected-access
"""Tests for the plugin manager."""
from unittest import mock
import importlib
import sys
from types import ModuleType
import pytest

from app.commands.command import Command
from app.plugins.plugin_interface import PluginInterface
from app.plugins.plugin_manager import PluginManager


class MockCommand(Command):
    """Mock command for testing."""

    @property
    def name(self):
        return "mock_command"

    def execute(self):
        return self.a + self.b


class MockPlugin(PluginInterface):
    """Mock plugin for testing."""

    @classmethod
    def get_name(cls):
        return "mock"

    @classmethod
    def get_plugin_type(cls):
        return "operation"

    @classmethod
    def get_command_class(cls):
        return MockCommand


class AnotherMockPlugin(PluginInterface):
    """Another mock plugin for testing."""

    @classmethod
    def get_name(cls):
        return "another_mock"

    @classmethod
    def get_plugin_type(cls):
        return "format"

    @classmethod
    def get_command_class(cls):
        return MockCommand


def test_plugin_manager_init():
    """Test plugin manager initialization."""
    manager = PluginManager()
    assert not manager._plugins


def create_mock_module(name="mock_module", plugins=None):
    """Create a mock module with plugins."""
    if plugins is None:
        plugins = [MockPlugin]

    mock_module = ModuleType(name)
    for plugin in plugins:
        setattr(mock_module, plugin.__name__, plugin)

    return mock_module


@mock.patch('importlib.import_module')
def test_register_plugins_from_module(mock_import):
    """Test registering plugins from a module."""
    # Create plugin manager
    manager = PluginManager()

    # Create mock module with plugin
    mock_module = create_mock_module()

    # Register plugins from module
    manager._register_plugins_from_module(mock_module)

    # Verify plugin was registered
    assert 'operation' in manager._plugins
    assert 'mock' in manager._plugins['operation']
    assert manager._plugins['operation']['mock'] == MockPlugin


@mock.patch('importlib.import_module')
@mock.patch('pkgutil.iter_modules')
def test_discover_plugins(mock_iter_modules, mock_import):
    """Test discovering plugins in a package."""
    # Create plugin manager
    manager = PluginManager()

    # Mock package
    mock_package = mock.MagicMock()
    mock_package.__path__ = ['mock_path']
    mock_package.__name__ = 'mock_package'
    mock_import.return_value = mock_package

    # Mock iter_modules to return a module
    mock_iter_modules.return_value = [
        ('loader', 'mock_module', False)  # (loader, name, is_pkg)
    ]

    # Mock importing the module
    mock_module = create_mock_module()
    mock_import.side_effect = [mock_package, mock_module]

    # Discover plugins
    manager.discover_plugins('mock_package')

    # Verify plugin was registered
    assert 'operation' in manager._plugins
    assert 'mock' in manager._plugins['operation']
    assert manager._plugins['operation']['mock'] == MockPlugin


@mock.patch('importlib.import_module')
@mock.patch('pkgutil.iter_modules')
def test_discover_plugins_with_subpackage(mock_iter_modules, mock_import):
    """Test discovering plugins in a package with subpackages."""
    # Create plugin manager
    manager = PluginManager()

    # Mock packages
    mock_package = mock.MagicMock()
    mock_package.__path__ = ['mock_path']
    mock_package.__name__ = 'mock_package'

    mock_subpackage = mock.MagicMock()
    mock_subpackage.__path__ = ['mock_subpath']
    mock_subpackage.__name__ = 'mock_package.mock_subpackage'

    # Mock iter_modules to return a subpackage and then a module
    mock_iter_modules.side_effect = [
        [('loader', 'mock_package.mock_subpackage', True)],  # For package
        [('loader', 'mock_package.mock_subpackage.mock_module', False)]  # For subpackage
    ]

    # Mock importing the modules
    mock_module = create_mock_module()
    mock_import.side_effect = [mock_package, mock_subpackage, mock_module]

    # Discover plugins
    manager.discover_plugins('mock_package')

    # Verify plugin was registered
    assert 'operation' in manager._plugins
    assert 'mock' in manager._plugins['operation']
    assert manager._plugins['operation']['mock'] == MockPlugin


def test_get_plugins():
    """Test getting plugins by type."""
    # Create plugin manager
    manager = PluginManager()

    # Manually register plugins
    mock_module = create_mock_module(plugins=[MockPlugin, AnotherMockPlugin])
    manager._register_plugins_from_module(mock_module)

    # Get all plugins
    all_plugins = manager.get_plugins()
    assert len(all_plugins) == 2
    assert all_plugins['mock'] == MockPlugin
    assert all_plugins['another_mock'] == AnotherMockPlugin

    # Get operation plugins
    operation_plugins = manager.get_plugins('operation')
    assert len(operation_plugins) == 1
    assert operation_plugins['mock'] == MockPlugin

    # Get format plugins
    format_plugins = manager.get_plugins('format')
    assert len(format_plugins) == 1
    assert format_plugins['another_mock'] == AnotherMockPlugin

    # Get nonexistent plugin type
    nonexistent_plugins = manager.get_plugins('nonexistent')
    assert nonexistent_plugins == {}


def test_get_plugin():
    """Test getting a specific plugin."""
    # Create plugin manager
    manager = PluginManager()

    # Manually register plugins
    mock_module = create_mock_module(plugins=[MockPlugin, AnotherMockPlugin])
    manager._register_plugins_from_module(mock_module)

    # Get specific plugins
    operation_plugin = manager.get_plugin('operation', 'mock')
    format_plugin = manager.get_plugin('format', 'another_mock')

    assert operation_plugin == MockPlugin
    assert format_plugin == AnotherMockPlugin

    # Get nonexistent plugin
    nonexistent_plugin = manager.get_plugin('operation', 'nonexistent')
    assert nonexistent_plugin is None
