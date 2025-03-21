"""Unit tests for the Calculator class."""
#pylint: disable= unused-import, no-member, protected-access
import unittest
import os
import shutil
import tempfile
import logging
from unittest.mock import patch, MagicMock, mock_open
from decimal import Decimal
import pandas as pd
from app.calculator import Calculator
from app.plugins import get_plugin_manager


class TestCalculator(unittest.TestCase): #pylint: disable= too-many-public-methods
    """Tests for Calculator class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test data
        self.test_data_dir = tempfile.mkdtemp()
        self.test_history_file = os.path.join(self.test_data_dir, "test_history.csv")

        # Create a calculator instance with the test history file
        self.calculator = Calculator(history_file=self.test_history_file)

    def tearDown(self):
        """Clean up after each test."""
        # Remove the test history file if it exists
        if os.path.exists(self.test_history_file):
            os.remove(self.test_history_file)

        # Remove the test data directory
        try:
            os.rmdir(self.test_data_dir)
        except OSError:
            # If directory not empty, use shutil.rmtree
            shutil.rmtree(self.test_data_dir, ignore_errors=True)

    def test_add(self):
        """Test addition operation."""
        result = self.calculator.add(Decimal('5'), Decimal('3'))
        self.assertEqual(result, Decimal('8'))

    def test_subtract(self):
        """Test subtraction operation."""
        result = self.calculator.subtract(Decimal('10'), Decimal('4'))
        self.assertEqual(result, Decimal('6'))

    def test_multiply(self):
        """Test multiplication operation."""
        result = self.calculator.multiply(Decimal('6'), Decimal('7'))
        self.assertEqual(result, Decimal('42'))

    def test_divide(self):
        """Test division operation."""
        result = self.calculator.divide(Decimal('20'), Decimal('5'))
        self.assertEqual(result, Decimal('4'))

    def test_divide_by_zero(self):
        """Test division by zero raises ValueError."""
        with self.assertRaises(ValueError):
            self.calculator.divide(Decimal('10'), Decimal('0'))

    def test_history_recording(self):
        """Test that operations are recorded in history."""
        # Perform operations
        self.calculator.add(Decimal('5'), Decimal('3'))
        self.calculator.multiply(Decimal('4'), Decimal('2'))

        # Get history
        history = self.calculator.get_history()

        # Check that history contains 2 records
        self.assertEqual(len(history), 2)

        # Check that the history file exists
        self.assertTrue(os.path.exists(self.test_history_file))

        # Check that the CSV file contains the correct data
        df = pd.read_csv(self.test_history_file)
        self.assertEqual(len(df), 2)

        # Check first record: add 5 + 3 = 8
        self.assertEqual(df.iloc[0]['operation'], 'add')
        self.assertEqual(df.iloc[0]['a'], 5.0)
        self.assertEqual(df.iloc[0]['b'], 3.0)
        self.assertEqual(df.iloc[0]['result'], 8.0)

        # Check second record: multiply 4 * 2 = 8
        self.assertEqual(df.iloc[1]['operation'], 'multiply')
        self.assertEqual(df.iloc[1]['a'], 4.0)
        self.assertEqual(df.iloc[1]['b'], 2.0)
        self.assertEqual(df.iloc[1]['result'], 8.0)

    def test_clear_history(self):
        """Test clearing history."""
        # Add some operations to history
        self.calculator.add(Decimal('5'), Decimal('3'))
        self.calculator.multiply(Decimal('4'), Decimal('2'))

        # Verify history has 2 records
        self.assertEqual(len(self.calculator.get_history()), 2)

        # Clear history
        self.calculator.clear_history()

        # Verify history is empty
        self.assertEqual(len(self.calculator.get_history()), 0)

        # Check that the CSV file is empty (except for headers)
        df = pd.read_csv(self.test_history_file)
        self.assertEqual(len(df), 0)

    def test_delete_history_record(self):
        """Test deleting a specific history record."""
        # Add some operations to history
        self.calculator.add(Decimal('5'), Decimal('3'))
        self.calculator.multiply(Decimal('4'), Decimal('2'))
        self.calculator.subtract(Decimal('10'), Decimal('3'))

        # Verify history has 3 records
        self.assertEqual(len(self.calculator.get_history()), 3)

        # Delete the second record (multiply operation)
        self.calculator.delete_history_record(1)

        # Verify history now has 2 records
        history = self.calculator.get_history()
        self.assertEqual(len(history), 2)

        # Check that the remaining records are correct
        operations = [row['operation'] for _, row in history.iterrows()]
        self.assertEqual(operations, ['add', 'subtract'])

        # Check the CSV file also has the correct data
        df = pd.read_csv(self.test_history_file)
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df['operation']), ['add', 'subtract'])

    def test_get_history_list(self):
        """Test getting formatted history list."""
        # Add some operations to history
        self.calculator.add(Decimal('5'), Decimal('3'))
        self.calculator.subtract(Decimal('10'), Decimal('4'))

        # Get formatted history list
        history_list = self.calculator.get_history_list()

        # Check that the list has 2 items
        self.assertEqual(len(history_list), 2)

        # Check the formatting
        self.assertEqual(history_list[0], "5.0 + 3.0 = 8.0")
        self.assertEqual(history_list[1], "10.0 - 4.0 = 6.0")

    def test_get_pandas_history_with_limit(self):
        """Test getting history with a limit."""
        # Add several operations to history
        self.calculator.add(Decimal('1'), Decimal('1'))
        self.calculator.add(Decimal('2'), Decimal('2'))
        self.calculator.add(Decimal('3'), Decimal('3'))
        self.calculator.add(Decimal('4'), Decimal('4'))

        # Get limited history (last 2 records)
        limited_history = self.calculator.get_pandas_history(limit=2)

        # Check that only 2 records are returned
        self.assertEqual(len(limited_history), 2)

        # Check that they are the most recent records
        self.assertEqual(limited_history.iloc[0]['a'], 3.0)
        self.assertEqual(limited_history.iloc[1]['a'], 4.0)

    def test_reload_plugins(self):
        """Test reloading plugins."""
        # This test simply verifies that the method doesn't raise an exception
        try:
            self.calculator.reload_plugins()
            succeeded = True
        except Exception: #pylint: disable= broad-exception-caught
            succeeded = False

        self.assertTrue(succeeded)

    def test_delete_history_record_index_out_of_range(self):
        """Test deleting a history record with an out-of-range index."""
        # Add a record to history
        self.calculator.add(Decimal('5'), Decimal('3'))

        # Attempt to delete with an out-of-range index
        with self.assertRaises(ValueError):
            self.calculator.delete_history_record(10)

        with self.assertRaises(ValueError):
            self.calculator.delete_history_record(-1)

    def test_get_history_list_empty(self):
        """Test getting history list when history is empty."""
        # Make sure history is empty
        self.calculator.clear_history()

        # Get history list
        history_list = self.calculator.get_history_list()

        # Verify it's an empty list
        self.assertEqual(history_list, [])

    def test_get_pandas_history_with_no_limit(self):
        """Test getting pandas history without a limit."""
        # Add some operations
        self.calculator.add(Decimal('1'), Decimal('1'))
        self.calculator.add(Decimal('2'), Decimal('2'))

        # Get history without limit
        history = self.calculator.get_pandas_history()

        # Verify all records are returned
        self.assertEqual(len(history), 2)

    def test_get_pandas_history_with_high_limit(self):
        """Test getting pandas history with a limit higher than number of records."""
        # Add some operations
        self.calculator.add(Decimal('1'), Decimal('1'))
        self.calculator.add(Decimal('2'), Decimal('2'))

        # Get history with high limit
        history = self.calculator.get_pandas_history(limit=10)

        # Verify all records are returned
        self.assertEqual(len(history), 2)

    def test_get_available_operations(self):
        """Test getting available operations."""
        operations = self.calculator.get_available_operations()

        # Verify it's a dictionary
        self.assertIsInstance(operations, dict)

        # Verify it contains at least the basic operations
        self.assertIn('add', operations)
        self.assertIn('subtract', operations)
        self.assertIn('multiply', operations)
        self.assertIn('divide', operations)

        # Verify the values are all 'operation'
        for op_type in operations.values():
            self.assertEqual(op_type, 'operation')

    @patch('app.calculator.pd.read_csv')
    def test_load_history_file_error(self, mock_read_csv):
        """Test loading history when file reading fails."""
        # Set up the mock to raise an exception
        mock_read_csv.side_effect = Exception("Test error")

        # Create a new calculator to test load history
        test_file = os.path.join(self.test_data_dir, "error_test.csv")

        # Create an empty file to read
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("timestamp,operation,a,b,result\n")

        # Create calculator to trigger loading
        calc = Calculator(history_file=test_file)

        # Verify history is empty (default when loading fails)
        self.assertEqual(len(calc.get_history()), 0)

    @patch('app.calculator.pd.DataFrame.to_csv')
    def test_save_history_direct_error(self, mock_to_csv):
        """Test saving history when direct file writing fails."""
        # Set up the mock to raise an exception
        mock_to_csv.side_effect = Exception("Test error")

        # Add an operation - this should trigger saving
        try:
            self.calculator.add(Decimal('5'), Decimal('3'))
            # No exception should propagate
            succeeded = True
        except Exception: #pylint: disable= broad-exception-caught
            succeeded = False

        self.assertTrue(succeeded)

    def test_initialize_with_existing_file(self):
        """Test initializing calculator with an existing history file."""
        # Create a history file with some data
        test_file = os.path.join(self.test_data_dir, "existing_history.csv")

        # Create a DataFrame with test data
        test_data = pd.DataFrame({
            'timestamp': ['2025-03-18 10:00:00'],
            'operation': ['add'],
            'a': [5.0],
            'b': [3.0],
            'result': [8.0]
        })

        # Save to CSV
        test_data.to_csv(test_file, index=False)

        # Create calculator with this history file
        calc = Calculator(history_file=test_file)

        # Verify the history was loaded
        history = calc.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history.iloc[0]['operation'], 'add')

    def test_clear_history_plugin_not_found(self):
        """Test clearing history when clear plugin is not found."""
        # Add an operation
        self.calculator.add(Decimal('5'), Decimal('3'))

        # Mock get_plugin to return None for clear_history
        original_get_plugin = self.calculator.plugin_manager.get_plugin

        def mock_get_plugin(plugin_type, plugin_name):
            if plugin_type == 'history' and plugin_name == 'clear_history':
                return None
            return original_get_plugin(plugin_type, plugin_name)

        self.calculator.plugin_manager.get_plugin = mock_get_plugin

        # Clear history - should use fallback
        self.calculator.clear_history()

        # Verify history is cleared
        self.assertEqual(len(self.calculator.get_history()), 0)

        # Restore original get_plugin
        self.calculator.plugin_manager.get_plugin = original_get_plugin

    def test_delete_history_record_plugin_not_found(self):
        """Test deleting history record when delete plugin is not found."""
        # Create a dataframe with known operations
        test_data = pd.DataFrame({
            'timestamp': ['2025-03-18 10:00:00', '2025-03-18 10:01:00'],
            'operation': ['add', 'multiply'],
            'a': [5.0, 4.0],
            'b': [3.0, 2.0],
            'result': [8.0, 8.0]
        })

        # Set the history data directly to ensure known operations
        self.calculator._history_data = test_data

        # Check initial state
        initial_history = self.calculator.get_history()
        self.assertEqual(len(initial_history), 2)
        self.assertEqual(initial_history.iloc[0]['operation'], 'add')
        self.assertEqual(initial_history.iloc[1]['operation'], 'multiply')

        # Mock get_plugin to return None for delete_history_record
        original_get_plugin = self.calculator.plugin_manager.get_plugin

        def mock_get_plugin(plugin_type, plugin_name):
            if plugin_type == 'history' and plugin_name == 'delete_history_record':
                return None
            return original_get_plugin(plugin_type, plugin_name)

        self.calculator.plugin_manager.get_plugin = mock_get_plugin

        # Delete the first record (index 0)
        self.calculator.delete_history_record(0)

        # Verify one record was deleted
        history = self.calculator.get_history()
        self.assertEqual(len(history), 1)

        # Verify the right record remains
        self.assertEqual(history.iloc[0]['operation'], 'multiply')

        # Restore original get_plugin
        self.calculator.plugin_manager.get_plugin = original_get_plugin

    def test_history_with_unknown_operation(self):
        """Test history list formatting with unknown operation."""
        # Manually add a record with an unknown operation
        unknown_record = {
            'timestamp': '2025-03-18 10:00:00',
            'operation': 'unknown_op',
            'a': 5.0,
            'b': 3.0,
            'result': 8.0
        }

        self.calculator._history_data = pd.DataFrame([unknown_record])

        # Get history list
        history_list = self.calculator.get_history_list()

        # Verify formatting
        self.assertEqual(history_list[0], "unknown_op(5.0, 3.0) = 8.0")

    def test_empty_history_data_on_save(self):
        """Test saving when history data is not a DataFrame."""
        # Set history data to None
        self.calculator._history_data = None

        # Save - should create an empty DataFrame
        self.calculator._save_history()

        # Verify history data is now a DataFrame
        self.assertIsInstance(self.calculator._history_data, pd.DataFrame)

    @patch('app.calculator.os.makedirs')
    @patch('pandas.DataFrame.to_csv')
    def test_directory_creation_on_init(self, mock_to_csv, mock_makedirs):
        """Test directory creation during initialization."""
        # Create a calculator to trigger directory creation
        # With both makedirs and to_csv mocked, no file operations will occur
        test_file = os.path.join(self.test_data_dir, "subdir", "test.csv")
        Calculator(history_file=test_file)

        # Verify makedirs was called with the right arguments
        mock_makedirs.assert_any_call(os.path.dirname(test_file), exist_ok=True)


if __name__ == '__main__':
    unittest.main()
