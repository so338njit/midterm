"""Tests for package initialization modules."""
# pylint: disable=unused-import
import pytest
from app import Calculator
from app.commands import CommandHandler, Command
from app.plugins import get_plugin_manager, PluginInterface
# Import these at the top level to avoid the import-outside-toplevel warning
from app.plugins.operations import AddPlugin, SubtractPlugin, MultiplyPlugin, DividePlugin


def test_calculator_package_init():
    """Test the calculator package initialization."""
    # Verify that Calculator is imported correctly
    assert isinstance(Calculator(), Calculator)


def test_commands_package_init():
    """Test the commands package initialization."""
    # Verify CommandHandler is imported correctly
    assert isinstance(CommandHandler(), CommandHandler)

    # Verify Command is imported correctly
    assert hasattr(Command, '__abstractmethods__')


def test_plugins_package_init():
    """Test the plugins package initialization."""
    # Verify get_plugin_manager returns the same instance each time
    manager1 = get_plugin_manager()
    manager2 = get_plugin_manager()
    assert manager1 is manager2

    # Verify PluginInterface is imported correctly
    assert hasattr(PluginInterface, '__abstractmethods__')


def test_operations_package_init():
    """Test the operations package initialization."""
    # This is mostly testing that imports don't raise errors
    # The imports are now at the top of the file

    # Verify plugin classes
    assert AddPlugin.get_name() == "add"
    assert SubtractPlugin.get_name() == "subtract"
    assert MultiplyPlugin.get_name() == "multiply"
    assert DividePlugin.get_name() == "divide"
