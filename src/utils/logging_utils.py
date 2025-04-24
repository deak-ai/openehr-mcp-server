"""
Logging utilities for the openEHR MCP server and related components.
"""
import logging
import time
import os
from pathlib import Path

# Configure standard logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Initialize root logger - only log to stdout
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """
    Get a logger with the specified name and consistent formatting.
    
    Args:
        name: The name of the logger, typically __name__ or component name
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    return logger

def log_incoming_message(logger, message_type, content=None, **kwargs):
    """
    Log an incoming message with consistent format.
    
    Args:
        logger: The logger instance
        message_type: Type of message (e.g., 'HTTP Request', 'Agent Request')
        content: Full message content
        **kwargs: Additional fields to log
    """
    extra_fields = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(
        f"INCOMING {message_type}: {content or ''} {extra_fields}"
    )

def log_outgoing_message(logger, message_type, content=None, **kwargs):
    """
    Log an outgoing message with consistent format.
    
    Args:
        logger: The logger instance
        message_type: Type of message (e.g., 'HTTP Response', 'Agent Response')
        content: Full message content
        **kwargs: Additional fields to log
    """
    extra_fields = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(
        f"OUTGOING {message_type}: {content or ''} {extra_fields}"
    )

def format_message(message):
    """
    Format a message for logging without truncation.
    
    Args:
        message: The message to format
        
    Returns:
        Formatted message string
    """
    if not message:
        return ""
    
    return str(message)
