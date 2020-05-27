# coding: utf-8
from os.path import exists
import logging.config
import json

messages = None


def initialize_logger(config_path='resources/logging_config.json', logs_file_path='resources/appLogs.log'):
    """Loads the logger"""

    if exists(logs_file_path):
        open(logs_file_path, 'w').close()

    if exists(config_path):
        with open(config_path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        logging.getLogger("loggerInitializer").info("Logger initialization : success")
    else:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger("loggerInitializer").info(
            "Logger initialization : error (Loaded default config: INFO level)")


def initialize_messages_config(config_path='resources/messages.json'):
    """"Loads messages configuration"""
    global messages

    with open(config_path, 'rt', encoding="utf-8") as f:
        messages = json.load(f)

    logging.getLogger(__name__).info('Message configuration initialized !')
