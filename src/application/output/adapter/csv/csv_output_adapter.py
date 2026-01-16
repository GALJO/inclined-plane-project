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
from typing import Any

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
SUFFIX_ERROR = "_error"
SUFFIX_REL_ERROR = "_rerror"
SUFFIX_VALUE = "_value"
SUFFIX_X = "_x"
SUFFIX_Y = "_y"


class CsvOutputAdapter(OutputPort):
    """OutputPort adapter for saving an output to a CSV file.

    Attributes
    ----------
    path: Path: Path to the target file.
    """

    def __init__(self, output_path: Path):
        """Constructor.

        :param output_path: Path: Path to the target file.
        """
        self.path: Path = output_path

    def send_output(self, measured: list[Result], model: list[Result], error: list[Error]) -> None:
        """Parses output to a CSV table and saves it to a target file.

        :param measured: list[Result]: Results from a simulation.
        :param model: list[Result]: Results from a model.
        :param error: list[Error]: Errors.
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
    """Updates each dictionary from output with corresponding dictionary from inp.

    :param output: tuple: Is updated.
    :param inp: tuple: Update data.

    """
    for i in range(0, len(output)):
        output[i].update(inp[i])


def get_any_dict(key: str, data) -> dict:
    """Creates CSV dict {key: data}.

    :param key: str: CSV header.
    :param data: CSV row.
    :returns: {key: data} dict.

    """
    return {key: data}


def get_scalar_dicts(key: str, measured: Scalar, model: Scalar, error: ScalarError) -> tuple[
    dict[str, float], dict[str, float], dict[str, Any]]:
    """Creates a CSV dict for Scalar values group.

    :param key: str: CSV header for group.
    :param measured: Scalar: Measured value.
    :param model: Scalar: Model value.
    :param error: ScalarError: Errors.
    :returns: Dictionaries {key_measured: measured} {key_model: model} {key_error: error.abs, key_rerror: error.rel}

    """
    return (
        {key + SUFFIX_MEASURED: measured.value},
        {key + SUFFIX_MODEL: model.value},
        {key + SUFFIX_ERROR: error.abs.value, key + SUFFIX_REL_ERROR: error.rel.value}
    )


def get_vector_dicts(key: str, measured: Vector, model: Vector, error: VectorError) -> tuple[
    dict[str, str], dict[str, str], dict[str, str]]:
    """Creates a CSV dict for Vector values group.

    :param key: str: CSV header for group.
    :param measured: Vector: Measured value.
    :param model: Vector: Model value.
    :param error: VectorError: Errors.
    :returns: Dictionaries {[measured values]} {[model values]} {[error values]}

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
    """Creates a full CSV row dict.

    :param measured: Result: Measured.
    :param model: Result: Model.
    :param error: Error: Errors.
    :returns: Dictionary representing one CSV row.
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
