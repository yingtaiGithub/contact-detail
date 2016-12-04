from scrapy_app.settings import LOG_DIR
from os import path
import sys
import logging

def configure_logging():
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_log = logging.StreamHandler()
    console_log.setLevel(logging.INFO)
    console_log.setFormatter(formatter)

    file_info_debug = logging.FileHandler(filename=path.join(LOG_DIR, 'log_debug.log'), mode='w', encoding='utf-8')
    file_info_debug.setLevel(logging.DEBUG)
    file_info_debug.setFormatter(formatter)

    file_warning_log = logging.FileHandler(filename=path.join(LOG_DIR, 'log_error.log'), mode='a', encoding='utf-8')
    file_warning_log.setLevel(logging.WARNING)
    file_warning_log.setFormatter(formatter)

    file_info_log = logging.FileHandler(filename=path.join(LOG_DIR, 'log_info.log'), mode='a', encoding='utf-8')
    file_info_log.setLevel(logging.INFO)
    file_info_log.setFormatter(formatter)

    logging.basicConfig(handlers=(file_info_debug,), level=logging.DEBUG)
    logger = logging.getLogger()
    logger.addHandler(console_log)
    logger.addHandler(file_warning_log)
    logger.addHandler(file_info_log)