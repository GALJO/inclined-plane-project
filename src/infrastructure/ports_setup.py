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
from infrastructure.constants import OUTPUT_PORT, OUTPUT_CSV_PATH


class AppPorts:
    def __init__(self):
        self.output_port = configure_output_port()


def configure_output_port():
    match OUTPUT_PORT:
        case "CSV":
            logging.info("Chosen output configuration: CSV")
            return CsvOutputAdapter(Path(OUTPUT_CSV_PATH))
        case _:
            logging.critical("ABORTING INIT - unknown LOG_LEVEL constant.")
            exit(1)
