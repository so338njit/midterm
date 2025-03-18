"""Integration tests for the calculator plugin system."""
# pylint: disable=no-member, unused-import
import sys
import importlib
from decimal import Decimal
import pytest
from app import Calculator
from app.plugins import get_plugin_manager


class TestAddingNewPlugin:
    """Test adding a new plugin to the system."""

    def test_dynamic_plugin_loading(self, tmp_path):
        """Test that a new plugin can be dynamically loaded."""
        # Create a new plugin file in a temporary directory
        plugin_dir = tmp_path / "plugins" / "operations"
        plugin_dir.mkdir(parents=True)

        # Create an __init__.py file to make it a proper package
        with open(plugin_dir / "__init__.py", "w", encoding="utf-8") as f:
            f.write("# Package initialization")

        # Create a modulo operation plugin
        with open(plugin_dir / "modulo.py", "w", encoding="utf-8") as f:
            f.write("""
from decimal import Decimal
from typing import Type
from app.commands.command import Command
from app.plugins.plugin_interface import PluginInterface


class ModuloCommand(Command):
    \"\"\"Command for modulo operation.\"\"\"

    @property
    def name(self) -> str:
        \"\"\"Name of the command.\"\"\"
        return "modulo"

    def execute(self) -> Decimal:
        \"\"\"Perform modulo operation.\"\"\"
        if self.b == 0:
            raise ValueError("Modulo by zero is not allowed")
        return Decimal(float(self.a) % float(self.b))

    def __repr__(self):
        \"\"\"String representation.\"\"\"
        return f"ModuloCommand({self.a}, {self.b})"


class ModuloPlugin(PluginInterface):
    \"\"\"Plugin for modulo operation.\"\"\"

    @classmethod
    def get_name(cls) -> str:
        \"\"\"Return the name of the plugin.\"\"\"
        return "modulo"

    @classmethod
    def get_plugin_type(cls) -> str:
        \"\"\"Return the type of the plugin.\"\"\"
        return "operation"

    @classmethod
    def get_command_class(cls) -> Type[Command]:
        \"\"\"Return the command class for this operation.\"\"\"
        return ModuloCommand
""")

        # Add the temp directory to the Python path so we can import from it
        sys.path.insert(0, str(tmp_path))

        try:
            # Import the module to register it
            importlib.import_module("plugins.operations.modulo")

            # Create a calculator and reload plugins to pick up the new one
            calc = Calculator()
            calc.plugin_manager.discover_plugins("plugins.operations")
            calc.reload_plugins()

            # Verify the new operation is available
            available_ops = calc.get_available_operations()
            assert "modulo" in available_ops

            # Test the new operation
            result = calc.modulo(Decimal('10'), Decimal('3'))
            assert float(result) == pytest.approx(1.0)

            # Test division by zero error
            with pytest.raises(ValueError, match="Modulo by zero is not allowed"):
                calc.modulo(Decimal('10'), Decimal('0'))

        finally:
            # Clean up the sys.path
            sys.path.remove(str(tmp_path))


def test_plugin_discovery():
    """Test the plugin discovery process."""
    # Get the plugin manager
    manager = get_plugin_manager()

    # Discover plugins
    manager.discover_plugins("calculator.plugins.operations")

    # Verify operations are found
    operation_plugins = manager.get_plugins("operation")
    assert "add" in operation_plugins
    assert "subtract" in operation_plugins
    assert "multiply" in operation_plugins
    assert "divide" in operation_plugins

    # Verify we can get specific plugins
    add_plugin = manager.get_plugin("operation", "add")
    assert add_plugin.get_name() == "add"

    # Verify we can instantiate and use a command from a plugin
    command_class = add_plugin.get_command_class()
    command = command_class(Decimal('7'), Decimal('3'))
    result = command.execute()
    assert result == Decimal('10')


def test_calculator_end_to_end():
    """End-to-end test of the calculator with plugins."""
    # Create a calculator
    calc = Calculator()

    # Test basic operations
    assert calc.add(Decimal('5'), Decimal('3')) == Decimal('8')
    assert calc.subtract(Decimal('10'), Decimal('4')) == Decimal('6')
    assert calc.multiply(Decimal('6'), Decimal('7')) == Decimal('42')
    assert calc.divide(Decimal('20'), Decimal('5')) == Decimal('4')

    # Test with negative numbers
    assert calc.add(Decimal('-5'), Decimal('8')) == Decimal('3')
    assert calc.subtract(Decimal('3'), Decimal('5')) == Decimal('-2')
    assert calc.multiply(Decimal('-3'), Decimal('-4')) == Decimal('12')
    assert calc.divide(Decimal('-12'), Decimal('4')) == Decimal('-3')

    # Test with decimal numbers
    assert calc.add(Decimal('3.5'), Decimal('2.7')) == Decimal('6.2')
    assert calc.subtract(Decimal('5.5'), Decimal('2.2')) == Decimal('3.3')
    assert calc.multiply(Decimal('2.5'), Decimal('4')) == Decimal('10.0')
    assert calc.divide(Decimal('10'), Decimal('2.5')) == Decimal('4')

    # Test the power operation if available
    try:
        assert float(calc.power(Decimal('2'), Decimal('3'))) == pytest.approx(8.0)
    except AttributeError:
        pass  # Power might not be loaded

    # Test history tracking
    history_df = calc.get_history()
    assert len(history_df) >= 2  # At least the operations we just performed

    # Test history contains the right types of operations
    operation_names = set(history_df['operation'])
    assert 'add' in operation_names
    assert 'subtract' in operation_names
    assert 'multiply' in operation_names
    assert 'divide' in operation_names