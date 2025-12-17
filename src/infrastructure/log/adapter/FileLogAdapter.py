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
from pathlib import Path

from infrastructure.log.LogPort import LogPort
from infrastructure.log.utils.logging_utils import get_loglevel, FORMAT
from infrastructure.log.utils.pre_logging import INIT_LOG


class FileLogAdapter(LogPort):
    """
    LoggingPort adapter for logging to file.
    """

    def __init__(self, _level: str, _path: Path):
        """
        Constructor.
        :param _level: Minimum level of log to be shown.
        :param _path: Path to log file.
        """
        self.log_level = get_loglevel(_level)
        self.log_path = _path.absolute()

    def setup(self):
        """
        Activate logging to file.
        """
        logging.warning(f"Pre-setup log end. From now on logging to file: log_file={self.log_path}")
        logger = logging.getLogger()
        logger.handlers.clear()

        ch = logging.FileHandler(self.log_path, "w")
        ch.setLevel(self.log_level)
        ch.setFormatter(logging.Formatter(FORMAT))
        logger = logging.getLogger()
        logger.setLevel(self.log_level)
        logger.addHandler(ch)
        logging.info(f"Logging to file activated: log_level={self.log_level} file_path={self.log_path}")
        logging.warning(f"Pre-setup logs are available at {INIT_LOG.absolute()}")
