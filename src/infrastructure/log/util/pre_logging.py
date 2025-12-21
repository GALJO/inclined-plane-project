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
import os.path
from logging import DEBUG

from infrastructure.log.util.get_level import FORMAT

from infrastructure.config.init_config import INIT_CONFIG


def init_pre_logging() -> None:
    """ """
    os.makedirs(os.path.dirname(INIT_CONFIG.prelog_path.absolute()), exist_ok=True)
    ch = logging.FileHandler(INIT_CONFIG.prelog_path.absolute(), "w")
    ch.setLevel(DEBUG)
    ch.setFormatter(logging.Formatter(FORMAT))
    logger = logging.getLogger()
    logger.setLevel(DEBUG)
    logger.handlers.clear()
    logger.addHandler(ch)
    logging.warning(f"Pre-setup log activated: log_file={INIT_CONFIG.prelog_path.absolute()}")
