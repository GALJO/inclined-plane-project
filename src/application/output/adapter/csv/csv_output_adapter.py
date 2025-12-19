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
import csv
import logging
import os
from pathlib import Path

from application.math.scalar import Scalar
from application.math.vector import Vector
from application.output.output_port import OutputPort
from application.result.error import Error, ScalarError, VectorError
from application.result.result import Result

CYCLE_NUMBER = "cycle_number"
IS_FULL = "is_full"
DURATION1 = "duration1"
DURATION2 = "duration2"
DURATION = "duration"
START_VELOCITY = "start_velocity"
END_VELOCITY = "end_velocity"
REACH = "reach"

SUFFIX_MEASURED = "_measured"
SUFFIX_MODEL = "_model"
PREFIX_ERROR = "error_"
PREFIX_RELATIVE_ERROR = "error_rel_"
SUFFIX_VALUE = "_value"
SUFFIX_X = "_x"
SUFFIX_Y = "_y"


class CsvOutputAdapter(OutputPort):
    """
    OutputPort adapter for saving data to CSV file.
    Attributes
    ----------
    path: Path
        Path object specifying path to CSV output file.
    """

    def __init__(self, output_path: Path):
        self.path: Path = output_path

    def send_output(self, measured: list[Result], model: list[Result], error: list[Error]) -> None:
        """
        Saves output to CSV file specified in path
        :param measured: A list of measured Result objects.
        :param model: A list of model Result objects.
        :param error: A list of Error objects for given Result objects.
        """
        logging.info(f"Saving results to CSV file: measured={measured} model={model} error={error}")
        os.makedirs(os.path.dirname(self.path.absolute()), exist_ok=True)
        with open(self.path.absolute(), "w", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=get_dict(measured[0], model[0], error[0]).keys())
            writer.writeheader()
            logging.debug(f"Wrote CSV headers: {writer.fieldnames}")
            for i in range(0, len(model)):
                row = get_dict(measured[i], model[i], error[i])
                writer.writerow(row)
                logging.debug(f"Wrote row: n={i} row={row}")
        logging.info(f"Output saved: rows={len(model)} path={self.path.absolute()}")


def dictionaries_update(output: tuple, inp: tuple) -> None:
    """
    Updates each dictionary in output tuple with corresponding dictionary in inp tuple.
    :param output: Being updated.
    :param inp: Update data.
    """
    for i in range(0, len(output)):
        output[i].update(inp[i])


def get_any_dict(key: str, data) -> dict:
    """
    Creates default dict for CSV output.
    :param key: Dictionary key (CSV header).
    :param data: Dictionary value (CSV row).
    :return: Dictionary (CSV).
    """
    return {key: data}


def get_scalar_dicts(key: str, measured: Scalar, model: Scalar, error: ScalarError) -> tuple[
    dict[str, str], dict[str, str], dict[str, str]]:
    """
    Creates dict from Scalar data for CSV output.
    :param key: Scalar value name (CSV headers).
    :param measured: Measured Scalar (CSV row).
    :param model: Model Scalar (CSV row).
    :param error: ScalarError object for given Scalars (CSV row).
    :return: Measure, model and error dictionary.
    """
    return (
        {key + SUFFIX_MEASURED: measured.value},
        {key + SUFFIX_MODEL: model.value},
        {PREFIX_ERROR + key: error.abs.value, PREFIX_RELATIVE_ERROR + key: error.rel.value}
    )


def get_vector_dicts(key: str, measured: Vector, model: Vector, error: VectorError) -> tuple[
    dict[str, str], dict[str, str], dict[str, str]]:
    """
    Creates dict from Vector data for CSV output.
    :param key: Vector value name (CSV headers).
    :param measured: Measured Vector (CSV row).
    :param model: Model Vector (CSV row).
    :param error: VectorError object for given Vectors (CSV row).
    :return: Measure, model and error dictionary.
    """
    measure_dict = {}
    model_dict = {}
    error_dict = {}
    dictionaries_update((measure_dict, model_dict, error_dict),
                        get_scalar_dicts(key + SUFFIX_X, measured.x, model.x, error.x))
    dictionaries_update((measure_dict, model_dict, error_dict),
                        get_scalar_dicts(key + SUFFIX_Y, measured.y, model.y, error.y))
    dictionaries_update((measure_dict, model_dict, error_dict),
                        get_scalar_dicts(key + SUFFIX_VALUE, measured.value, model.value, error.value))
    return measure_dict, model_dict, error_dict


def get_dict(measured: Result, model: Result, error: Error) -> dict:
    """
    Creates a dict from Result data for CSV output.
    :param measured: Measured Result.
    :param model: Model Result
    :param error: Results Error object.
    :return: Dictionary ready for CSV parsing.
    """
    result = {}
    measure_dict = {}
    model_dict = {}
    error_dict = {}

    dictionaries_update((measure_dict, model_dict, error_dict),
                        get_scalar_dicts(DURATION1, measured.duration1, model.duration1, error.duration1))
    dictionaries_update((measure_dict, model_dict, error_dict),
                        get_scalar_dicts(DURATION2, measured.duration2, model.duration2, error.duration2))
    dictionaries_update((measure_dict, model_dict, error_dict),
                        get_scalar_dicts(DURATION, measured.duration, model.duration, error.duration))

    dictionaries_update((measure_dict, model_dict, error_dict),
                        get_vector_dicts(START_VELOCITY, measured.start_velocity, model.start_velocity,
                                         error.start_velocity))
    dictionaries_update((measure_dict, model_dict, error_dict),
                        get_vector_dicts(END_VELOCITY, measured.end_velocity, model.end_velocity, error.end_velocity))
    dictionaries_update((measure_dict, model_dict, error_dict),
                        get_vector_dicts(REACH, measured.reach, model.reach, error.reach))

    result.update(get_any_dict(CYCLE_NUMBER, model.number))
    result.update(measure_dict)
    result.update(model_dict)
    result.update(error_dict)
    result.update(get_any_dict(IS_FULL, model.is_full))
    logging.debug(f"Created output row: dict={result} measured={measured} model={model} error={error}")
    return result
