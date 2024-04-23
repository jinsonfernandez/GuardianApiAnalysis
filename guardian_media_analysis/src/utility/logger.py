import os
import logging
from datetime import datetime

def setup_logger(logger_name):
    """
    This function creates a seprate folder for each day and within each day creates all log files that are run on that day
    Args:
        logger_name(str) : The name of logger
    Returns:
        logging.Logger: logger instance that is configured
    """
    current_date = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_directory = os.path.join("logs", current_date)
    os.makedirs(log_directory, exist_ok=True)

    logger= logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    log_file = os.path.join(log_directory,f"{logger_name}_{timestamp}.log")
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger
