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

from application.output.adapter.csv.CsvOutputAdapter import CsvOutputAdapter
from infrastructure.config.Config import CONFIG
from infrastructure.log.adapter.ConsoleLogAdapter import ConsoleLogAdapter
from infrastructure.log.adapter.FileLogAdapter import FileLogAdapter


class AppPorts:
    def __init__(self):
        self.log_port = configure_log_port()
        self.output_port = configure_output_port()


def configure_log_port():
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


def configure_output_port():
    match CONFIG.output_port:
        case "CSV":
            logging.info("Chosen output configuration: CSV")
            if CONFIG.output_path is None:
                logging.critical("INIT FAIL -- no output.path config.")
            return CsvOutputAdapter(CONFIG.output_path)
        case _:
            logging.critical("INIT FAIL -- unknown output.port config.")
            exit(1)
