"""Tests for the CommandHandler class."""
# pylint: disable=unused-import
from decimal import Decimal
from unittest import mock
import pytest
from app.commands.command_handler import CommandHandler
from app.commands.command import Command

class SampleCommand(Command):
    """Test command implementation."""

    def __init__(self, a, b, name="test_command"):
        """Initialize with custom name."""
        super().__init__(a, b)
        self._name = name

    @property
    def name(self) -> str:
        """Return the command name."""
        return self._name

    def execute(self) -> Decimal:
        """Execute the command."""
        return self.a + self.b

    def __repr__(self):
        """Return string representation."""
        return f"TestCommand({self.a}, {self.b})"


def test_command_handler_initialization():
    """Test CommandHandler initialization."""
    handler = CommandHandler()
    assert not handler.history


def test_command_handler_execute(decimal_values):
    """Test executing a command with the handler."""
    a, b = decimal_values['a'], decimal_values['b']
    handler = CommandHandler()
    command = SampleCommand(a, b)

    result = handler.execute(command)

    # Verify result
    assert result == a + b

    # Verify command was added to history
    assert len(handler.history) == 1
    assert handler.history[0] == command


def test_command_handler_get_history():
    """Test getting the command history."""
    handler = CommandHandler()
    cmd1 = SampleCommand(Decimal('1'), Decimal('2'))
    cmd2 = SampleCommand(Decimal('3'), Decimal('4'))

    # Execute commands
    handler.execute(cmd1)
    handler.execute(cmd2)

    # Get history
    history = handler.get_history()

    # Verify history
    assert len(history) == 2
    assert history[0] == cmd1
    assert history[1] == cmd2


def test_command_handler_clear_history():
    """Test clearing the command history."""
    handler = CommandHandler()
    cmd = SampleCommand(Decimal('1'), Decimal('2'))

    # Execute command
    handler.execute(cmd)
    assert len(handler.history) == 1

    # Clear history
    handler.clear_history()
    assert len(handler.history) == 0


def test_command_handler_get_latest():
    """Test getting the most recent command."""
    handler = CommandHandler()

    # Empty history
    assert handler.get_latest() is None

    # Add commands
    cmd1 = SampleCommand(Decimal('1'), Decimal('2'))
    cmd2 = SampleCommand(Decimal('3'), Decimal('4'))
    handler.execute(cmd1)
    handler.execute(cmd2)

    # Get latest
    latest = handler.get_latest()
    assert latest == cmd2


def test_command_handler_find_by_command_name():
    """Test finding commands by name."""
    handler = CommandHandler()

    # Add commands with different names
    cmd1 = SampleCommand(Decimal('1'), Decimal('2'), name="add")
    cmd2 = SampleCommand(Decimal('3'), Decimal('4'), name="subtract")
    cmd3 = SampleCommand(Decimal('5'), Decimal('6'), name="add")

    handler.execute(cmd1)
    handler.execute(cmd2)
    handler.execute(cmd3)

    # Find by name
    add_cmds = handler.find_by_command_name("add")
    subtract_cmds = handler.find_by_command_name("subtract")
    multiply_cmds = handler.find_by_command_name("multiply")

    # Verify results
    assert len(add_cmds) == 2
    assert cmd1 in add_cmds
    assert cmd3 in add_cmds

    assert len(subtract_cmds) == 1
    assert cmd2 in subtract_cmds

    assert len(multiply_cmds) == 0

@mock.patch('app.commands.command_handler.MAX_HISTORY_SIZE', 3)
def test_history_size_limit():
    """Test that history is limited to max size."""
    handler = CommandHandler()

    # Add more commands than the max limit
    for i in range(5):
        cmd = SampleCommand(Decimal(i), Decimal(i))
        handler.execute(cmd)

    # Check that only the most recent commands are kept
    assert len(handler.get_history()) == 3

    # Verify the oldest commands were removed
    history = handler.get_history()
    assert history[0].a == Decimal(2)
    assert history[1].a == Decimal(3)
    assert history[2].a == Decimal(4)
