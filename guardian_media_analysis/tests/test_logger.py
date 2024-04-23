import os
from src.utility import setup_logger
from datetime import datetime
import logging

class TestSetupLogger:
    def test_create_logger(self):
        logger_name = "test_logger"
        logger = setup_logger(logger_name)
        assert isinstance(logger, logging.Logger)
        assert logger.name == logger_name

    def test_log_file_creation(self):
        logger_name = "test_logger"
        logger = setup_logger(logger_name)
        current_date = datetime.now().strftime("%Y%m%d")
        log_directory = os.path.join("logs", current_date)
        assert os.path.exists(log_directory)

    def test_log_message_formatting(self):
        logger_name = "test_logger"
        logger = setup_logger(logger_name)
        test_message = "Test message"
        logger.info(test_message)
        current_date = datetime.now().strftime("%Y%m%d")
        log_directory = os.path.join("logs", current_date)
        log_files = os.listdir(log_directory)
        assert len(log_files) == 1
        log_file = log_files[0]
        assert log_file.startswith(logger_name)
        assert current_date in log_file
        with open(os.path.join(log_directory, log_file), "r") as file:
            content = file.read()
            assert test_message in content

    def test_logging_multiple_messages(self):
        logger_name = "test_logger"
        logger = setup_logger(logger_name)
        logger.warning("Test warning message")
        logger.error("Test error message")
        current_date = datetime.now().strftime("%Y%m%d")
        log_directory = os.path.join("logs", current_date)
        log_files = os.listdir(log_directory)
        log_file = log_files[0]
        with open(os.path.join(log_directory, log_file), "r") as file:
            content = file.read()
            assert "Test warning message" in content
            assert "Test error message" in content

    def test_creating_multiple_loggers(self):
        logger_name = "test_logger"
        another_logger_name = "another_test_logger"
        logger = setup_logger(logger_name)
        another_logger = setup_logger(another_logger_name)
        assert isinstance(another_logger, logging.Logger)
        assert another_logger.name == another_logger_name
        another_test_message = "Another test message"
        another_logger.info(another_test_message)
        current_date = datetime.now().strftime("%Y%m%d")
        log_directory = os.path.join("logs", current_date)
        log_files = os.listdir(log_directory)
        assert len(log_files) == 2
        another_log_file = [f for f in log_files if f.startswith(another_logger_name)][0]
        with open(os.path.join(log_directory, another_log_file), "r") as file:
            content = file.read()
            assert another_test_message in content

    def teardown_method(self, method):
        current_date = datetime.now().strftime("%Y%m%d")
        log_directory = os.path.join("logs", current_date)
        log_files = os.listdir(log_directory)
        for log_file in log_files:
            os.remove(os.path.join(log_directory, log_file))
        os.rmdir(log_directory)