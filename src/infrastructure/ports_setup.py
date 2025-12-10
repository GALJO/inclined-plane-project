import logging
from pathlib import Path

from application.output.adapter.csv.CsvOutputAdapter import CsvOutputAdapter
from infrastructure.constants import OUTPUT_PORT, CSV_PATH


class AppPorts:
    def __init__(self):
        self.output_port = configure_output_port()


def configure_output_port():
    match OUTPUT_PORT:
        case "CSV":
            logging.info("Chosen output configuration: CSV")
            return CsvOutputAdapter(Path(CSV_PATH))
        case _:
            logging.critical("ABORTING INIT - unknown LOG_LEVEL constant.")
            exit(1)
