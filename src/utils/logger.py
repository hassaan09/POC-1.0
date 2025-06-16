"""
Logging configuration for the application
"""
import logging
import os
from datetime import datetime

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """Setup logger with file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler(f'logs/{log_file}')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger