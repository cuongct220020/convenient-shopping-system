# shared/shopping_shared/utils/logger_utils.py

import logging
import sys
from logging.handlers import RotatingFileHandler

# ANSI Color Codes
class Colors:
    DEBUG = '\033[94m'    # Blue
    INFO = '\033[92m'     # Green
    WARNING = '\033[93m'  # Yellow
    ERROR = '\033[91m'    # Red
    CRITICAL = '\033[1;91m' # Bold Red
    RESET = '\033[0m'
    GREY = '\033[90m'

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to console logs based on level."""
    
    def __init__(self, fmt: str, datefmt: str):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.FORMATS = {
            logging.DEBUG: f"{Colors.GREY}%(asctime)s{Colors.RESET} {Colors.DEBUG}[%(levelname)s]{Colors.RESET} [{Colors.DEBUG}%(name)s{Colors.RESET}] - %(message)s",
            logging.INFO: f"{Colors.GREY}%(asctime)s{Colors.RESET} {Colors.INFO}[%(levelname)s]{Colors.RESET} [{Colors.INFO}%(name)s{Colors.RESET}] - %(message)s",
            logging.WARNING: f"{Colors.GREY}%(asctime)s{Colors.RESET} {Colors.WARNING}[%(levelname)s]{Colors.RESET} [{Colors.WARNING}%(name)s{Colors.RESET}] - %(message)s",
            logging.ERROR: f"{Colors.GREY}%(asctime)s{Colors.RESET} {Colors.ERROR}[%(levelname)s]{Colors.RESET} [{Colors.ERROR}%(name)s{Colors.RESET}] - %(message)s",
            logging.CRITICAL: f"{Colors.GREY}%(asctime)s{Colors.RESET} {Colors.CRITICAL}[%(levelname)s]{Colors.RESET} [{Colors.CRITICAL}%(name)s{Colors.RESET}] - %(message)s",
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self._style._fmt)
        formatter = logging.Formatter(log_fmt, self.datefmt)
        return formatter.format(record)

# Standard configuration
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s'
DATE_FORMAT = '%m-%d-%Y %H:%M:%S %Z'
LOG_FILE = 'logging.log'

def get_console_handler():
    """Returns a console handler with colored output."""
    console_handler = logging.StreamHandler(sys.stdout)
    # Use ColoredFormatter for console
    console_handler.setFormatter(ColoredFormatter(LOG_FORMAT, DATE_FORMAT))
    return console_handler

def get_file_handler():
    """Returns a file handler with plain text output."""
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5) # 10MB
    # Use standard Formatter for file (ANSI codes look bad in text files)
    file_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))
    return file_handler

def get_logger(logger_name: str, level: int = logging.DEBUG):
    """Creates a logger with both console and (optional) file handlers."""
    logger = logging.getLogger(logger_name)
    
    if not logger.hasHandlers():
        logger.setLevel(level)
        logger.addHandler(get_console_handler())
        # Tùy chọn: Thêm file handler nếu muốn lưu log ra file
        # logger.addHandler(get_file_handler())

    # Prevent logs from bubbling up to the root logger twice
    logger.propagate = False
    
    return logger
