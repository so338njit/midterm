"""Tests for operation plugins."""
from decimal import Decimal
import pytest
from app.plugins.operations.add import AddCommand, AddPlugin
from app.plugins.operations.subtract import SubtractCommand, SubtractPlugin
from app.plugins.operations.multiply import MultiplyCommand, MultiplyPlugin
from app.plugins.operations.divide import DivideCommand, DividePlugin


class TestAddOperation:
    """Tests for the Add operation."""

    def test_add_command_name(self):
        """Test the name property of AddCommand."""
        cmd = AddCommand(Decimal('1'), Decimal('2'))
        assert cmd.name == "add"

    def test_add_command_execute(self, decimal_values):
        """Test executing the AddCommand."""
        a, b = decimal_values['a'], decimal_values['b']
        cmd = AddCommand(a, b)
        result = cmd.execute()
        assert result == a + b

    def test_add_command_repr(self):
        """Test the string representation of AddCommand."""
        cmd = AddCommand(Decimal('10'), Decimal('5'))
        assert str(cmd) == "AddCommand(10, 5)"

    def test_add_plugin(self):
        """Test the AddPlugin class."""
        assert AddPlugin.get_name() == "add"
        assert AddPlugin.get_plugin_type() == "operation"
        assert AddPlugin.get_command_class() == AddCommand


class TestSubtractOperation:
    """Tests for the Subtract operation."""

    def test_subtract_command_name(self):
        """Test the name property of SubtractCommand."""
        cmd = SubtractCommand(Decimal('1'), Decimal('2'))
        assert cmd.name == "subtract"

    def test_subtract_command_execute(self, decimal_values):
        """Test executing the SubtractCommand."""
        a, b = decimal_values['a'], decimal_values['b']
        cmd = SubtractCommand(a, b)
        result = cmd.execute()
        assert result == a - b

    def test_subtract_command_repr(self):
        """Test the string representation of SubtractCommand."""
        cmd = SubtractCommand(Decimal('10'), Decimal('5'))
        assert str(cmd) == "SubtractCommand(10, 5)"

    def test_subtract_plugin(self):
        """Test the SubtractPlugin class."""
        assert SubtractPlugin.get_name() == "subtract"
        assert SubtractPlugin.get_plugin_type() == "operation"
        assert SubtractPlugin.get_command_class() == SubtractCommand


class TestMultiplyOperation:
    """Tests for the Multiply operation."""

    def test_multiply_command_name(self):
        """Test the name property of MultiplyCommand."""
        cmd = MultiplyCommand(Decimal('1'), Decimal('2'))
        assert cmd.name == "multiply"

    def test_multiply_command_execute(self, decimal_values):
        """Test executing the MultiplyCommand."""
        a, b = decimal_values['a'], decimal_values['b']
        cmd = MultiplyCommand(a, b)
        result = cmd.execute()
        assert result == a * b

    def test_multiply_command_repr(self):
        """Test the string representation of MultiplyCommand."""
        cmd = MultiplyCommand(Decimal('10'), Decimal('5'))
        assert str(cmd) == "MultiplyCommand(10, 5)"

    def test_multiply_plugin(self):
        """Test the MultiplyPlugin class."""
        assert MultiplyPlugin.get_name() == "multiply"
        assert MultiplyPlugin.get_plugin_type() == "operation"
        assert MultiplyPlugin.get_command_class() == MultiplyCommand


class TestDivideOperation:
    """Tests for the Divide operation."""

    def test_divide_command_name(self):
        """Test the name property of DivideCommand."""
        cmd = DivideCommand(Decimal('1'), Decimal('2'))
        assert cmd.name == "divide"

    def test_divide_command_execute(self, decimal_values):
        """Test executing the DivideCommand."""
        a, b = decimal_values['a'], decimal_values['b']
        cmd = DivideCommand(a, b)
        result = cmd.execute()
        assert result == a / b

    def test_divide_command_division_by_zero(self, decimal_values):
        """Test division by zero raises ValueError."""
        a, zero = decimal_values['a'], decimal_values['zero']
        cmd = DivideCommand(a, zero)
        with pytest.raises(ValueError, match="Division by zero is not allowed"):
            cmd.execute()

    def test_divide_command_repr(self):
        """Test the string representation of DivideCommand."""
        cmd = DivideCommand(Decimal('10'), Decimal('5'))
        assert str(cmd) == "DivideCommand(10, 5)"

    def test_divide_plugin(self):
        """Test the DividePlugin class."""
        assert DividePlugin.get_name() == "divide"
        assert DividePlugin.get_plugin_type() == "operation"
        assert DividePlugin.get_command_class() == DivideCommand
