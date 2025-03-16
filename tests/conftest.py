"""Configuration for pytest."""
import os
import sys
from decimal import Decimal
import pytest

# Add the project root to the Python path so we can import from calculator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def decimal_values():
    """Provide common decimal values for testing."""
    return {
        'a': Decimal('10'),
        'b': Decimal('5'),
        'zero': Decimal('0'),
        'negative': Decimal('-3'),
        'fraction': Decimal('0.5')
    }
