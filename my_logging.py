import logging
from logging import config
import sys
from os import path


def checked_load_logging_config(config_path):
    expanded_config_path = path.expanduser(config_path)
    if not path.exists(expanded_config_path):
        raise Exception(
            "failed to locate a logging configuration at [%s]. please check the location" % expanded_config_path)
    logging.config.fileConfig(expanded_config_path)


def basic_logger_config():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def get_logger(name):
    return logging.getLogger(name)