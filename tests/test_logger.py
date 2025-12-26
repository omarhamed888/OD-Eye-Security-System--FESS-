import pytest
from src.utils.logger import setup_logger
import os

def test_logger_setup():
    """Test logger initialization and file creation."""
    logger = setup_logger("test_logger", "DEBUG")
    assert logger.name == "test_logger"
    assert logger.level == 10 # DEBUG level
    
    # Test logging doesn't crash
    logger.info("Test message")
    logger.error("Test error")

def test_logger_file_handler():
    """Ensure log directory is created."""
    log_dir = "logs"
    setup_logger("file_test", "INFO")
    assert os.path.exists(log_dir)
