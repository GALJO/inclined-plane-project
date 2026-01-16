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
from infrastructure.log.util.get_level import *
from infrastructure.log.util.get_level import get_level, FORMAT

from infrastructure.config.init_config import INIT_CONFIG
from infrastructure.log.log_port import LogPort


class ConsoleLogAdapter(LogPort):
    """LogPort adapter for console logging."""

    def __init__(self, _log_level: str):
        """
        Constructor.
        :param _log_level: Minimum level of log to be seen.
        """
        self.log_level = get_level(_log_level)

    def setup(self):
        """Activate logging to the console."""
        logging.warning(f"Pre-setup log end. From now on logging to console.")
        logger = logging.getLogger()
        logger.handlers.clear()

        ch = logging.StreamHandler()
        ch.setLevel(self.log_level)
        ch.setFormatter(ConsoleFormatter(FORMAT))
        logger.setLevel(self.log_level)
        logger.addHandler(ch)
        logging.info(f"Logging to console activated: log_level={self.log_level}")
        logging.warning(f"Pre-setup logs are available at {INIT_CONFIG.prelog_path.absolute()}")


class ConsoleFormatter(logging.Formatter):
    """Custom formatter for console logging."""

    def format(self, record: logging.LogRecord):
        """

        :param record: logging.LogRecord: 

        """
        white = '\033[97m'
        bold = '\033[91m'
        grey = '\033[37m'
        yellow = '\033[93m'
        red = '\033[31m'
        red_light = '\033[91m'
        start_style = {
            'DEBUG': grey,
            'INFO': white,
            'WARNING': yellow,
            'ERROR': red,
            'CRITICAL': red_light + bold,
        }.get(record.levelname, white)
        end_style = white
        return f'{start_style}{super().format(record)}{end_style}'
