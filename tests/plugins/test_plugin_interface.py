# pylint: disable = unused-import, invalid-name, abstract-class-instantiated
"""Tests for the plugin system."""
from decimal import Decimal
from typing import Type
from unittest.mock import patch
import logging
import pytest

from app.commands.command import Command
from app.plugins.plugin_interface import PluginInterface
from app.plugins.operations.add import AddCommand, AddPlugin
from app.plugins.operations.subtract import SubtractCommand, SubtractPlugin
from app.plugins.operations.multiply import MultiplyCommand, MultiplyPlugin
from app.plugins.operations.divide import DivideCommand, DividePlugin


def test_plugin_interface_abstract():
    """Test that PluginInterface is properly set up as an abstract interface."""
    # Attempting to instantiate PluginInterface directly should raise TypeError
    with pytest.raises(TypeError):
        PluginInterface()


def test_plugin_registration():
    """Test that all plugins can be properly registered and discovered."""
    # This test assumes you have a plugin registry mechanism
    # If not, you can adapt it to your actual plugin discovery method
    plugins = [AddPlugin, SubtractPlugin, MultiplyPlugin, DividePlugin]

    # Check that each plugin has the required interface methods
    for plugin in plugins:
        if hasattr(plugin, 'get_name'):
            assert isinstance(plugin.get_name(), str)

        if hasattr(plugin, 'get_plugin_type'):
            assert isinstance(plugin.get_plugin_type(), str)

        if hasattr(plugin, 'get_command_class'):
            assert issubclass(plugin.get_command_class(), Command)


class TestOperationPlugins:
    """Tests for operation plugins."""

    @pytest.mark.parametrize("plugin_class,command_class,expected_name", [
        (AddPlugin, AddCommand, "add"),
        (SubtractPlugin, SubtractCommand, "subtract"),
        (MultiplyPlugin, MultiplyCommand, "multiply"),
        (DividePlugin, DivideCommand, "divide"),
    ])
    def test_plugin_basics(self, plugin_class, command_class, expected_name):
        """Test basic plugin functionality."""
        # Test plugin name
        assert plugin_class.get_name() == expected_name

        # Test plugin type
        assert plugin_class.get_plugin_type() == "operation"

        # Test command class
        assert plugin_class.get_command_class() == command_class

    @pytest.mark.parametrize("plugin_class,a,b,expected", [
        (AddPlugin, Decimal('5'), Decimal('3'), Decimal('8')),
        (SubtractPlugin, Decimal('10'), Decimal('4'), Decimal('6')),
        (MultiplyPlugin, Decimal('6'), Decimal('7'), Decimal('42')),
        (DividePlugin, Decimal('20'), Decimal('5'), Decimal('4')),
    ])
    def test_plugin_execution(self, plugin_class, a, b, expected):
        """Test plugin execution through command class."""
        command_class = plugin_class.get_command_class()
        command = command_class(a, b)

        result = command.execute()
        assert result == expected


def test_divide_by_zero():
    """Test division by zero error handling in DividePlugin."""
    command_class = DividePlugin.get_command_class()
    command = command_class(Decimal('10'), Decimal('0'))

    with pytest.raises(ValueError) as exc_info:
        command.execute()

    assert "Division by zero is not allowed" in str(exc_info.value)


def test_plugin_logging():
    """Test that plugins properly implement logging."""
    with patch('logging.Logger.debug') as mock_debug:
        # Test logging in add command
        cmd = AddPlugin.get_command_class()(Decimal('5'), Decimal('3'))
        cmd.execute()
        assert mock_debug.called
