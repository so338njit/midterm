#pylint: disable = unused-import
"""Tests for the base Command class."""
from decimal import Decimal
import inspect
from unittest import mock
from abc import abstractmethod
import pytest

from app.commands.command import Command
from app.plugins.operations.add import AddCommand


class ConcreteCommand(Command):
    """Concrete implementation of Command for testing."""

    @property
    def name(self) -> str:
        """Return the name of the command."""
        return "test_command"

    def execute(self) -> Decimal:
        """Execute the command implementation."""
        return self.a + self.b


@pytest.fixture
def decimal_values():
    """Provide decimal values for tests."""
    return {'a': Decimal('10'), 'b': Decimal('5')}


def test_command_initialization(decimal_values):
    """Test that a Command can be initialized with two decimal values."""
    a, b = decimal_values['a'], decimal_values['b']
    cmd = ConcreteCommand(a, b)

    assert cmd.a == a
    assert cmd.b == b


def test_command_abstract_methods():
    """Test that Command is properly set up as an abstract class."""
    # Attempting to instantiate Command directly should raise TypeError
    with pytest.raises(TypeError):
        Command(Decimal('1'), Decimal('2'))  # pylint: disable=abstract-class-instantiated

    # Check that execute is an abstract method
    assert hasattr(Command, 'execute')
    assert getattr(Command.execute, '__isabstractmethod__', False) is True

    # Check that name is an abstract property
    assert hasattr(Command, 'name')

    # Verify abstract methods set
    assert 'execute' in Command.__abstractmethods__
    assert 'name' in Command.__abstractmethods__


def test_concrete_command_name():
    """Test that a concrete command implementation has a name property."""
    cmd = ConcreteCommand(Decimal('1'), Decimal('2'))
    assert cmd.name == "test_command"


def test_concrete_command_execute(decimal_values):
    """Test that a concrete command can be executed."""
    a, b = decimal_values['a'], decimal_values['b']
    cmd = ConcreteCommand(a, b)

    result = cmd.execute()
    assert result == a + b
    assert isinstance(result, Decimal)


@mock.patch('logging.Logger.debug')
def test_logging_integration(mock_debug):
    """Test logging integration with commands.

    This test assumes command implementations include logging.
    If not all commands implement logging yet, this can be adapted.
    """
    cmd = AddCommand(Decimal('5'), Decimal('3'))
    result = cmd.execute()

    assert result == Decimal('8')
    assert mock_debug.called
