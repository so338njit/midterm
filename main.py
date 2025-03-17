"""Command line interface for the Advanced Calculator with integrated History Management."""
import os
import sys
import pandas as pd
import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

from dotenv import load_dotenv
from app import Calculator
from app.plugins import get_plugin_manager
from app.config import DEBUG_MODE, DEFAULT_OUTPUT_FORMAT, DATA_DIRECTORY, CSV_HISTORY_FILE
from app.logging_setup import setup_logging

# Set up logging and load environment variables
logger = setup_logging()
load_dotenv()

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
MAX_HISTORY_SIZE = int(os.getenv("MAX_HISTORY_SIZE", "5"))
DECIMAL_PRECISION = int(os.getenv("DECIMAL_PRECISION", "10"))

# Ensure data directory exists
os.makedirs(DATA_DIRECTORY, exist_ok=True)


def process_command(calc, args):
    """Process a command in postfix notation (e.g., "4 3 add")"""
    if len(args) != 3:
        print("Error: Commands must have exactly 3 parts (e.g., '4 3 add')")
        return

    # Parse the operands
    try:
        a = Decimal(args[0])
        b = Decimal(args[1])
    except InvalidOperation:
        print("Error: Operands must be valid numbers")
        return

    # Get the operation
    operation = args[2].lower()

    # Execute the appropriate command
    try:
        if operation == "add":
            result = calc.add(a, b)
            print(f"{a} + {b} = {result}")
        elif operation == "subtract":
            result = calc.subtract(a, b)
            print(f"{a} - {b} = {result}")
        elif operation == "multiply":
            result = calc.multiply(a, b)
            print(f"{a} * {b} = {result}")
        elif operation == "divide":
            result = calc.divide(a, b)
            print(f"{a} / {b} = {result}")
        else:
            print(f"Error: Unknown operation '{operation}'")
            print("Supported operations: add, subtract, multiply, divide")
    except ValueError as e:
        print(f"Error: {e}")


def print_help():
    """Display help information"""
    print("Usage: python main.py [command]")
    print("\nBasic Commands:")
    print("  - Calculation in postfix notation: 4 3 add")
    print("  - history: Display calculation history")
    print("  - help: Display this help message")
    print("  - menu: Display all available plugin commands")
    print("  - exit: Exit the program")
    print("\nHistory Management Commands:")
    print("  - history-mode: Enter history management mode")
    print("  - history-load [file]: Load history from file")
    print("  - history-save [file]: Save history to file")
    print("  - history-clear: Clear all calculation history")
    print("  - history-delete <index>: Delete a specific history record")
    print("\nSupported operations: add, subtract, multiply, divide")
    print("Example: python main.py 10 5 divide")
    print(f"\nData directory: {DATA_DIRECTORY}")


def print_menu(calc):
    """Display menu information"""
    available_operations = calc.get_available_operations()

    if not available_operations:
        print("No plugins available")
        return

    print("\nAvailable Operations:")
    for operation_name, operation_type in available_operations.items():
        print(f" - {operation_name.capitalize()}: {operation_type}")


def show_history(calc, limit=None):
    """Display the calculation history"""
    history_df = calc.get_pandas_history(limit)

    if len(history_df) == 0:
        print("No calculations in history")
        return

    print("\nCalculation History:")
    history_list = calc.get_history_list()
    for idx, entry in enumerate(history_list, 1):
        print(f"{idx}. {entry}")


def show_detailed_history(calc, limit=None):
    """Display the detailed calculation history"""
    history = calc.get_pandas_history(limit)

    if len(history) == 0:
        print("No calculations in history")
        return

    print("\nDetailed Calculation History:")
    history.index.name = 'idx'
    history = history.reset_index()
    print(history.to_string())


def load_history(calc, file_path=None):
    """Load history from a specified file."""
    file_path = file_path or CSV_HISTORY_FILE

    # If a relative path is provided, make it relative to the data directory
    if not os.path.isabs(file_path):
        file_path = os.path.join(DATA_DIRECTORY, file_path)

    plugin_manager = get_plugin_manager()
    load_plugin = plugin_manager.get_plugin('history', 'load_history')

    if not load_plugin:
        print("Load history plugin not found")
        return

    command_class = load_plugin.get_command_class()
    command = command_class(kwargs={'file_path': file_path})

    try:
        # Access the private history data through the calculator instance
        calc._history_data = command.execute()
        print(f"Loaded {len(calc._history_data)} records from {file_path}")
    except Exception as e:
        print(f"Error loading history: {e}")


def save_history(calc, file_path=None):
    """Save history to a specified file."""
    file_path = file_path or CSV_HISTORY_FILE

    # If a relative path is provided, make it relative to the data directory
    if not os.path.isabs(file_path):
        file_path = os.path.join(DATA_DIRECTORY, file_path)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    plugin_manager = get_plugin_manager()
    save_plugin = plugin_manager.get_plugin('history', 'save_history')

    if not save_plugin:
        print("Save history plugin not found")
        return

    command_class = save_plugin.get_command_class()
    command = command_class(kwargs={'file_path': file_path, 'history_data': calc._history_data})

    try:
        command.execute()
        print(f"History saved to {file_path}")
    except Exception as e:
        print(f"Error saving history: {e}")


def add_history_record(calc, args):
    """Add a record to history manually."""
    parts = args.split()
    if len(parts) < 4:
        print("Usage: add <operation> <a> <b> <r>")
        return

    operation = parts[0]
    try:
        a = Decimal(parts[1])
        b = Decimal(parts[2])
        result = Decimal(parts[3])
    except (ValueError, IndexError):
        print("Invalid arguments. Usage: add <operation> <a> <b> <r>")
        return

    # Add to pandas history
    new_record = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'operation': operation,
        'a': float(a),
        'b': float(b),
        'result': float(result)
    }

    calc._history_data = pd.concat([calc._history_data, pd.DataFrame([new_record])], ignore_index=True)
    calc._save_history()
    print("Record added to history")


def history_mode(calc):
    """Enter history management mode with its own command prompt."""
    print("\nHistory Management Mode")
    print("Type 'help' for available commands or 'exit' to return to calculator")

    commands = {
        'load': lambda args: load_history(calc, args),
        'save': lambda args: save_history(calc, args),
        'add': lambda args: add_history_record(calc, args),
        'clear': lambda args: clear_history(calc, None),
        'delete': lambda args: delete_history_record(calc, args),
        'show': lambda args: show_history_with_limit(calc, args),
        'detail': lambda args: show_detailed_history_with_limit(calc, args),
        'help': lambda args: show_history_help(),
        'exit': lambda args: None  # Will exit the loop
    }

    running = True
    while running:
        try:
            command_line = input("history> ").strip()

            if not command_line:
                continue

            parts = command_line.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else None

            if command == 'exit':
                running = False
                print("Returning to calculator")
            elif command in commands:
                commands[command](args)
            else:
                print(f"Unknown command: {command}")
                show_history_help()

        except KeyboardInterrupt:
            print("\nReturning to calculator")
            running = False
        except Exception as e:
            print(f"Error: {e}")


def show_history_with_limit(calc, args=None):
    """Show history with optional limit."""
    limit = None
    if args:
        try:
            limit = int(args)
        except ValueError:
            print(f"Invalid limit: {args}, showing all records")

    show_history(calc, limit)


def show_detailed_history_with_limit(calc, args=None):
    """Show detailed history with optional limit."""
    limit = None
    if args:
        try:
            limit = int(args)
        except ValueError:
            print(f"Invalid limit: {args}, showing all records")

    show_detailed_history(calc, limit)


def show_history_help():
    """Display help information for history mode."""
    help_text = f"""
History Management Commands:
--------------------------
load [file_path]       - Load history from file (default: {CSV_HISTORY_FILE})
save [file_path]       - Save history to file (default: {CSV_HISTORY_FILE})
add <op> <a> <b> <r>   - Add a record to history
clear                  - Clear all history
delete <index>         - Delete record at index
show [limit]           - Show formatted history records
detail [limit]         - Show detailed history records
help                   - Show this help message
exit                   - Return to calculator

Data is stored in: {DATA_DIRECTORY}
"""
    print(help_text)


def clear_history(calc, args=None):
    """Clear all history data."""
    calc.clear_history()
    print("History cleared")


def delete_history_record(calc, args):
    """Delete a record at the specified index."""
    if not args:
        print("Usage: delete <index>")
        return

    try:
        index = int(args)
    except ValueError:
        print(f"Invalid index: {args}")
        return

    try:
        calc.delete_history_record(index)
        print(f"Record at index {index} deleted")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main function for the calculator CLI"""
    calc = Calculator()

    # Process command line arguments if provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "help":
            print_help()
        elif sys.argv[1] == "menu":
            print_menu(calc)
        elif sys.argv[1] == "history":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            show_history(calc, limit)
        elif sys.argv[1] == "history-detail":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            show_detailed_history(calc, limit)
        elif sys.argv[1] == "history-mode":
            history_mode(calc)
        elif sys.argv[1] == "history-load":
            file_path = sys.argv[2] if len(sys.argv) > 2 else None
            load_history(calc, file_path)
        elif sys.argv[1] == "history-save":
            file_path = sys.argv[2] if len(sys.argv) > 2 else None
            save_history(calc, file_path)
        elif sys.argv[1] == "history-clear":
            clear_history(calc)
        elif sys.argv[1] == "history-delete":
            if len(sys.argv) < 3:
                print("Error: Please specify an index to delete")
            else:
                delete_history_record(calc, sys.argv[2])
        else:
            process_command(calc, sys.argv[1:])
        return

    # Interactive mode
    print("Advanced Calculator - Interactive Mode")
    print("Enter commands in postfix notation (e.g., '4 3 add')")
    print("Type 'help' for more information, 'menu' to see available plugins, or 'exit' to quit")

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            args = user_input.split()
            command = args[0].lower()

            if command == "exit":
                break
            elif command == "help":
                print_help()
            elif command == "history":
                limit = int(args[1]) if len(args) > 1 else None
                show_history(calc, limit)
            elif command == "history-detail":
                limit = int(args[1]) if len(args) > 1 else None
                show_detailed_history(calc, limit)
            elif command == "history-mode":
                history_mode(calc)
            elif command == "history-load":
                file_path = args[1] if len(args) > 1 else None
                load_history(calc, file_path)
            elif command == "history-save":
                file_path = args[1] if len(args) > 1 else None
                save_history(calc, file_path)
            elif command == "history-clear":
                clear_history(calc)
            elif command == "history-delete":
                if len(args) < 2:
                    print("Error: Please specify an index to delete")
                else:
                    delete_history_record(calc, args[1])
            elif command == "menu":
                print_menu(calc)
            else:
                process_command(calc, args)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
