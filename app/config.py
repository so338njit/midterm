import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application configuration
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# History configuration
MAX_HISTORY_SIZE = int(os.getenv("MAX_HISTORY_SIZE", "5"))

# Data directory configuration
DATA_DIRECTORY = os.getenv("DATA_DIRECTORY", "data")
CSV_HISTORY_FILE = os.path.join(DATA_DIRECTORY, os.getenv("CSV_HISTORY_FILE", "calculator_history.csv"))

# Display configuration
DECIMAL_PRECISION = int(os.getenv("DECIMAL_PRECISION", "10"))
SCIENTIFIC_NOTATION_THRESHOLD = int(os.getenv("SCIENTIFIC_NOTATION_THRESHOLD", "10"))
DEFAULT_OUTPUT_FORMAT = os.getenv("DEFAULT_OUTPUT_FORMAT", "standard")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/calculator.log")
