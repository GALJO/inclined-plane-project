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
from infrastructure.config.config import OUTPUT_PORT, OUTPUT_PATH, LOG_PORT, LOG_LEVEL, LOG_PATH
from infrastructure.log.adapter.ConsoleLogAdapter import ConsoleLogAdapter
from infrastructure.log.adapter.FileLogAdapter import FileLogAdapter


class AppPorts:
    def __init__(self):
        self.log_port = configure_log_port()
        self.output_port = configure_output_port()


def configure_log_port():
    match LOG_PORT:
        case "CONSOLE":
            logging.info("Chosen log configuration: CONSOLE")
            return ConsoleLogAdapter(LOG_LEVEL)
        case "FILE":
            logging.info("Chosen log configuration: FILE")
            if LOG_PATH is None:
                logging.critical("EXIT -- unknown LOG_PATH config field.")
            return FileLogAdapter(LOG_LEVEL, Path(LOG_PATH))
        case _:
            logging.critical("EXIT -- unknown LOG_PORT config field.")
            exit(-201)


def configure_output_port():
    match OUTPUT_PORT:
        case "CSV":
            logging.info("Chosen output configuration: CSV")
            return CsvOutputAdapter(Path(OUTPUT_PATH))
        case _:
            logging.critical("EXIT -- unknown OUTPUT_PORT config field.")
            exit(-202)
