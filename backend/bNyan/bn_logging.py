


import logging
import sys
from . import util 

def get_logger(name : str, log_file : str = "", log_level = logging.DEBUG):

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)-8s %(message)s", "%Y-%m-%d %H:%M:%S")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    
    if log_file:
        util.create_directory_from_file_name(log_file)
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.addHandler(stdout_handler)
    logger.setLevel(log_level)

    return logger

