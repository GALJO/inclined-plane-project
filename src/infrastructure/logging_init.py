"""
Copyright 2025 Jan Oleński

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing
permissions and limitations under the License.
"""
import logging
from time import sleep

from infrastructure.constants import LOG_LEVEL


def logging_init():
    """
    Initializes logging
    """
    _loglevel = get_loglevel(LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(_loglevel)
    ch.setFormatter(CustomFormatter("[%(asctime)s] [%(levelname)s] || [%(funcName)s] %(filename)s :: %(message)s"))
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(_loglevel)
    logger.addHandler(ch)
    sleep(0.1)
    logging.info("Logging activated")


class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        no_style = '\033[37m'
        bold = '\033[91m'
        grey = '\033[90m'
        yellow = '\033[93m'
        red = '\033[31m'
        red_light = '\033[91m'
        start_style = {
            'DEBUG': grey,
            'INFO': no_style,
            'WARNING': yellow,
            'ERROR': red,
            'CRITICAL': red_light + bold,
        }.get(record.levelname, no_style)
        end_style = no_style
        return f'{start_style}{super().format(record)}{end_style}'


def get_loglevel(_loglevel: str):
    match _loglevel:
        case "DEBUG":
            return logging.DEBUG
        case "INFO":
            return logging.INFO
        case "WARN":
            return logging.WARN
        case "ERROR":
            return logging.ERROR
        case "CRITICAL":
            return logging.CRITICAL
        case _:
            logging.critical("ABORTING INIT - unknown LOG_LEVEL constant.")
            exit(1)
