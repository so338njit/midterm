"""Example usage of the calculator with plugins."""
from decimal import Decimal
from app import Calculator

def main():
    """Demonstrate the calculator with plugin architecture."""
    # Create a calculator instance (this will load all plugins)
    calc = Calculator()

    # Print available operations
    print("Available operations:", calc.get_available_operations())

    # Perform some calculations using the dynamically loaded operations
    print("\nPerforming calculations:")
    print(f"2 + 3 = {calc.add(Decimal('2'), Decimal('3'))}")
    print(f"5 - 2 = {calc.subtract(Decimal('5'), Decimal('2'))}")
    print(f"4 * 6 = {calc.multiply(Decimal('4'), Decimal('6'))}")
    print(f"10 / 2 = {calc.divide(Decimal('10'), Decimal('2'))}")

    # If the power plugin is available, use it
    try:
        print(f"2^3 = {calc.power(Decimal('2'), Decimal('3'))}")
    except AttributeError:
        print("Power operation not available. Add the power.py plugin to enable it.")

    # Print the calculation history
    print("\nCalculation history:")
    for cmd in calc.get_history():
        print(f"- {cmd}")

if __name__ == "__main__":
    main()
