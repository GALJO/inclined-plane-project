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

from application.input.adapter.console_input_adapter import ConsoleInputAdapter
from application.output.adapter.csv.csv_output_adapter import CsvOutputAdapter
from infrastructure.config.config import CONFIG
from infrastructure.log.adapter.console_log_adapter import ConsoleLogAdapter
from infrastructure.log.adapter.file_log_adapter import FileLogAdapter


class AppPorts:
    """Contains ports."""

    def __init__(self):
        self.log = configure_log_port()
        self.input = configures_input_port()
        self.output = configure_output_port()


def configure_log_port():
    """Configures log port."""
    match CONFIG.log_port:
        case "CONSOLE":
            logging.info("Chosen log configuration: CONSOLE")
            return ConsoleLogAdapter(CONFIG.log_level)
        case "FILE":
            logging.info("Chosen log configuration: FILE")
            if CONFIG.output_path is None:
                logging.critical("INIT FAIL -- no log.path config.")
                exit(1)
            return FileLogAdapter(CONFIG.log_level, CONFIG.log_path)
        case _:
            logging.critical("INIT FAIL -- unknown log.port config.")
            exit(1)


def configures_input_port():
    """Configures input port."""
    match CONFIG.input.port:
        case "CONSOLE":
            logging.info("Chosen input configuration: CONSOLE")
            return ConsoleInputAdapter()
        case _:
            logging.critical("INIT FAIL -- unknown input.port config.")
            exit(1)


def configure_output_port():
    """Configures output port."""
    match CONFIG.output_port:
        case "CSV":
            logging.info("Chosen output configuration: CSV")
            if CONFIG.output_path is None:
                logging.critical("INIT FAIL -- no output.path config.")
            return CsvOutputAdapter(CONFIG.output_path)
        case _:
            logging.critical("INIT FAIL -- unknown output.port config.")
            exit(1)
