"""Centralized logging configuration"""

import logging
import sys


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    Setup and configure a logger with consistent formatting

    Args:
        name: Logger name
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
