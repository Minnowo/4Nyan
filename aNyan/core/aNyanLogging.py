import sys
import os
import logging

from . import aNyanConstants

LOGGER_INSTANCE = logging.getLogger(aNyanConstants.BRAND)

debug = LOGGER_INSTANCE.debug
info = LOGGER_INSTANCE.info 
warning = LOGGER_INSTANCE.warning
warn = LOGGER_INSTANCE.warn
error = LOGGER_INSTANCE.error
critical = LOGGER_INSTANCE.critical

def create_setup_logger(name: str = None, log_file: str = "", log_level=logging.DEBUG):

    if name:
        logger = logging.getLogger(name)

    else:
        logger = logging.getLogger()

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.addHandler(stdout_handler)
    logger.setLevel(log_level)

    return logger


def setup_logger(log_file: str = "", log_level=logging.DEBUG):

    create_setup_logger(aNyanConstants.BRAND, log_file, log_level)

def show_startup_message(message: str=None):

    LOGGER_INSTANCE.info("~[__^w^_  <3  <3")
    LOGGER_INSTANCE.info(f"4Nyan starting. Time: {aNyanConstants.START_TIME_PRETTY}")

    if message:
        LOGGER_INSTANCE.info(message)

def setup_and_show_startup_message(message: str=None, log_file: str = "", log_level=logging.DEBUG):

    setup_logger(log_file, log_level)
    show_startup_message(message)