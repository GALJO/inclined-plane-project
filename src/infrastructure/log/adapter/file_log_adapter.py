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
import os
from pathlib import Path

from infrastructure.log.util.get_level import get_level, FORMAT

from infrastructure.config.init_config import INIT_CONFIG
from infrastructure.log.log_port import LogPort


class FileLogAdapter(LogPort):
    """LogPort adapter for file logging."""

    def __init__(self, _level: str, _path: Path):
        """Constructor.

        :param _level: str: The log level.
        :param _path: Path: A target file's path.
        """
        self.log_level = get_level(_level)
        self.log_path = _path

    def setup(self):
        """Activate logging to a file."""
        logging.warning(f"Pre-setup log end. From now on logging to file: log_file={self.log_path.absolute()}")
        logger = logging.getLogger()
        logger.handlers.clear()

        os.makedirs(os.path.dirname(self.log_path.absolute()), exist_ok=True)
        ch = logging.FileHandler(self.log_path.absolute(), "w")
        ch.setLevel(self.log_level)
        ch.setFormatter(logging.Formatter(FORMAT))
        logger = logging.getLogger()
        logger.setLevel(self.log_level)
        logger.addHandler(ch)
        logging.info(f"Logging to file activated: log_level={self.log_level} file_path={self.log_path.absolute()}")
        logging.warning(f"Pre-setup logs are available at {INIT_CONFIG.prelog_path.absolute()}")
