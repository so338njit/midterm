"""Base command interface for the command pattern"""
from abc import ABC, abstractmethod
from decimal import Decimal

class Command(ABC):
    """Abstract base class for calculator commands"""

    def __init__(self, a: Decimal, b: Decimal):
        """Initialize with two operands"""
        self.a = a
        self.b = b

    @abstractmethod
    def execute(self) -> Decimal:
        """Execute the command and return the result"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the command"""
        pass
