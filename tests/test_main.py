"""Tests for the example.py main script."""
import sys
from decimal import Decimal
from unittest.mock import patch, MagicMock
import pytest

# Import the main function from example.py
sys.path.insert(0, '.')
try:
    from example import main
except ImportError:
    pytestmark = pytest.mark.skip("example.py not found")


@patch('builtins.print')
def test_main_function_basic(mock_print):
    """Basic test for main function - verify it runs without errors."""
    try:
        # Simply call the main function and verify it doesn't raise exceptions
        main()
        # Success if we get here
        assert True
    except Exception as e: # pylint: disable=broad-exception-caught
        pytest.fail(f"main() function raised an exception: {str(e)}")


@patch('example.Calculator')
def test_calculator_usage(mock_calculator_class):
    """Test that the main function creates and uses Calculator correctly."""
    # Create a mock calculator instance
    mock_calc = MagicMock()

    # Setup return values
    mock_calc.add.return_value = Decimal('5')
    mock_calc.subtract.return_value = Decimal('3')
    mock_calc.multiply.return_value = Decimal('24')
    mock_calc.divide.return_value = Decimal('5')
    mock_calc.get_available_operations.return_value = {"add": "operation"}
    mock_calc.get_history.return_value = []

    # Setup the calculator class mock to return our mock instance
    mock_calculator_class.return_value = mock_calc

    # Suppress print output during test
    with patch('builtins.print'):
        # Call the main function
        main()

    # Verify that calculator methods were called
    assert mock_calculator_class.called, "Calculator class wasn't instantiated"
    assert mock_calc.add.called, "Calculator.add wasn't called"
    assert mock_calc.subtract.called, "Calculator.subtract wasn't called"
    assert mock_calc.multiply.called, "Calculator.multiply wasn't called"
    assert mock_calc.divide.called, "Calculator.divide wasn't called"
    assert mock_calc.get_available_operations.called, "Calculator.get_available_operations wasn't called"
    assert mock_calc.get_history.called, "Calculator.get_history wasn't called"
