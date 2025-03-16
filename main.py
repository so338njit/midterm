"""Command line interface for the Advanced Calculator."""
import os
from decimal import Decimal, InvalidOperation
import sys
from app import Calculator
from dotenv import load_dotenv
from app.config import DEBUG_MODE, DEFAULT_OUTPUT_FORMAT, SAVE_HISTORY, HISTORY_FILE
from app.logging_setup import setup_logging

logger = setup_logging()
load_dotenv()

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
MAX_HISTORY_SIZE = int(os.getenv("MAX_HISTORY_SIZE", "5"))
DECIMAL_PRECISION = int(os.getenv("DECIMAL_PRECISION", "10"))

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
    print("\nCommands:")
    print("  - Calculation in postfix notation: 4 3 add")
    print("  - history: Display calculation history")
    print("  - help: Display this help message")
    print("  - exit: Exit the program")
    print("\nSupported operations: add, subtract, multiply, divide")
    print("Example: python main.py 10 5 divide")

def main():
    """Main function for the calculator CLI"""
    calc = Calculator()
    
    # Process command line arguments if provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "help":
            print_help()
        elif sys.argv[1] == "history":
            show_history(calc)
        else:
            process_command(calc, sys.argv[1:])
        return

    # Interactive mode
    print("Advanced Calculator - Interactive Mode")
    print("Enter commands in postfix notation (e.g., '4 3 add')")
    print("Type 'help' for more information or 'exit' to quit")
    
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
                show_history(calc)
            else:
                process_command(calc, args)
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def show_history(calc):
    """Display the calculation history"""
    history = calc.get_history()
    
    if not history:
        print("No calculations in history")
        return
        
    print("\nCalculation History:")
    for idx, command in enumerate(history, 1):
        print(f"{idx}. {command}")

if __name__ == "__main__":
    main()
