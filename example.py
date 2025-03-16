"""Example usage of the calculator with plugins."""
import logging
from decimal import Decimal
from app import Calculator
from app.logging_setup import setup_logging

# Set up logging
logger = setup_logging()

def main():
    """Demonstrate the calculator with plugin architecture."""
    logger.info("Starting calculator demonstration")

    # Create a calculator instance (this will load all plugins)
    calc = Calculator()
    logger.debug("Calculator instance created")

    # Print available operations
    operations = calc.get_available_operations()
    logger.info(f"Available operations: {operations}")
    print("Available operations:", operations)

    # Perform some calculations using the dynamically loaded operations
    logger.info("Performing calculations")
    print("\nPerforming calculations:")

    result = calc.add(Decimal('2'), Decimal('3'))
    logger.debug(f"Addition operation: 2 + 3 = {result}")
    print(f"2 + 3 = {result}")

    result = calc.subtract(Decimal('5'), Decimal('2'))
    logger.debug(f"Subtraction operation: 5 - 2 = {result}")
    print(f"5 - 2 = {result}")

    result = calc.multiply(Decimal('4'), Decimal('6'))
    logger.debug(f"Multiplication operation: 4 * 6 = {result}")
    print(f"4 * 6 = {result}")

    result = calc.divide(Decimal('10'), Decimal('2'))
    logger.debug(f"Division operation: 10 / 2 = {result}")
    print(f"10 / 2 = {result}")

    # If the power plugin is available, use it
    try:
        result = calc.power(Decimal('2'), Decimal('3'))
        logger.debug(f"Power operation: 2^3 = {result}")
        print(f"2^3 = {result}")
    except AttributeError as e:
        error_msg = "Power operation not available. Add the power.py plugin to enable it."
        logger.warning(f"{error_msg} Error: {str(e)}")
        print(error_msg)

    # Print the calculation history
    history = calc.get_history()
    logger.info(f"Retrieved calculation history with {len(history)} entries")
    print("\nCalculation history:")
    for cmd in history:
        print(f"- {cmd}")

    logger.info("Calculator demonstration completed")

if __name__ == "__main__":
    logger.info("Example script started")
    main()
    logger.info("Example script completed")
