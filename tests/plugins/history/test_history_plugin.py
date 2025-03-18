"""Unit tests for the History Plugin."""
import unittest
import os
import tempfile
import pandas as pd
from decimal import Decimal

from app.plugins.history.history_plugin import (
    LoadHistoryCommand,
    SaveHistoryCommand,
    ClearHistoryCommand,
    DeleteHistoryRecordCommand
)


class TestHistoryPlugin(unittest.TestCase):
    """Tests for the history plugin components."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test data
        self.test_data_dir = tempfile.mkdtemp()
        self.test_history_file = os.path.join(self.test_data_dir, "test_history.csv")

        # Create a sample DataFrame for testing
        self.sample_data = pd.DataFrame({
            'timestamp': ['2025-03-18 10:00:00', '2025-03-18 10:01:00', '2025-03-18 10:02:00'],
            'operation': ['add', 'multiply', 'subtract'],
            'a': [5.0, 3.0, 10.0],
            'b': [3.0, 4.0, 7.0],
            'result': [8.0, 12.0, 3.0]
        })

    def tearDown(self):
        """Clean up after each test."""
        # Remove the test history file if it exists
        if os.path.exists(self.test_history_file):
            os.remove(self.test_history_file)

        # Remove the test directory
        os.rmdir(self.test_data_dir)

    def test_save_history_command(self):
        """Test saving history to CSV file."""
        # Create a command to save history
        command = SaveHistoryCommand(
            history_data=self.sample_data,
            file_path=self.test_history_file
        )

        # Execute the command
        result = command.execute()

        # Verify the command returned True (success)
        self.assertTrue(result)

        # Verify the file was created
        self.assertTrue(os.path.exists(self.test_history_file))

        # Read the file and verify the content
        saved_data = pd.read_csv(self.test_history_file)

        # Check the saved DataFrame has the same shape
        self.assertEqual(saved_data.shape, self.sample_data.shape)

        # Check the content matches
        pd.testing.assert_frame_equal(
            saved_data.reset_index(drop=True), 
            self.sample_data.reset_index(drop=True),
            check_dtype=False  # CSV reading might change datatypes slightly
        )

    def test_load_history_command(self):
        """Test loading history from CSV file."""
        # First save some data
        self.sample_data.to_csv(self.test_history_file, index=False)

        # Create a command to load history
        command = LoadHistoryCommand(
            file_path=self.test_history_file
        )

        # Execute the command
        loaded_data = command.execute()

        # Verify the loaded data matches the original
        self.assertEqual(loaded_data.shape, self.sample_data.shape)
        pd.testing.assert_frame_equal(
            loaded_data.reset_index(drop=True), 
            self.sample_data.reset_index(drop=True),
            check_dtype=False  # CSV reading might change datatypes slightly
        )

    def test_load_history_command_file_not_found(self):
        """Test loading history from a non-existent file."""
        # Use a non-existent file path
        non_existent_file = os.path.join(self.test_data_dir, "non_existent.csv")

        # Create a command to load history
        command = LoadHistoryCommand(
            file_path=non_existent_file
        )

        # Execute the command
        loaded_data = command.execute()

        # Verify an empty DataFrame was returned
        self.assertEqual(loaded_data.shape[0], 0)
        self.assertEqual(set(loaded_data.columns), {'timestamp', 'operation', 'a', 'b', 'result'})

    def test_clear_history_command(self):
        """Test clearing history."""
        # Create a command to clear history
        command = ClearHistoryCommand()

        # Execute the command
        result = command.execute()

        # Verify the result is an empty DataFrame with the correct columns
        self.assertEqual(result.shape[0], 0)
        self.assertEqual(set(result.columns), {'timestamp', 'operation', 'a', 'b', 'result'})

    def test_delete_history_record_command(self):
        """Test deleting a specific record from history."""
        # Create a command to delete a record
        command = DeleteHistoryRecordCommand(
            history_data=self.sample_data,
            index=1  # Delete the second record (multiply operation)
        )

        # Execute the command
        result = command.execute()

        # Verify the result has one less record
        self.assertEqual(result.shape[0], self.sample_data.shape[0] - 1)

        # Verify the correct record was deleted
        self.assertEqual(list(result['operation']), ['add', 'subtract'])

        # Verify the indices were reset
        self.assertEqual(list(result.index), [0, 1])

    def test_delete_history_record_command_invalid_index(self):
        """Test deleting a record with an invalid index."""
        # Create a command with an out-of-range index
        command = DeleteHistoryRecordCommand(
            history_data=self.sample_data,
            index=10  # Out of range
        )

        # Verify the command raises ValueError
        with self.assertRaises(ValueError):
            command.execute()

    def test_save_history_command_invalid_data(self):
        """Test saving with invalid history data."""
        # Create a command with None as history_data
        command = SaveHistoryCommand(
            history_data=None,
            file_path=self.test_history_file
        )

        # Verify the command raises ValueError
        with self.assertRaises(ValueError):
            command.execute()

    def test_delete_history_record_command_invalid_data(self):
        """Test deleting with invalid history data."""
        # Create a command with None as history_data
        command = DeleteHistoryRecordCommand(
            history_data=None,
            index=0
        )

        # Verify the command raises ValueError
        with self.assertRaises(ValueError):
            command.execute()

    def test_delete_history_record_command_no_index(self):
        """Test deleting without providing an index."""
        # Create a command without an index
        command = DeleteHistoryRecordCommand(
            history_data=self.sample_data
        )

        # Verify the command raises ValueError
        with self.assertRaises(ValueError):
            command.execute()


if __name__ == '__main__':
    unittest.main()
