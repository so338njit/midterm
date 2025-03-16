"""Configure logging for the calculator application."""
import os
import logging
from app.config import LOG_LEVEL, LOG_FILE

def setup_logging():
    """Set up logging to file for the calculator application."""
    # Get log level from config
    log_level_name = LOG_LEVEL.upper()
    level = getattr(logging, log_level_name, logging.INFO)

    # Create formatter
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear any existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Add file handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    return root_logger
