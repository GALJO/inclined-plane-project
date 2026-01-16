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

from application.math.scalar import Scalar
from application.math.vector import Vector
from application.result.result import Result


class ScalarError:
    """A class containing a Scalar values' measurement error.

    Attributes
    ----------
    abs
        (Scalar) Absolute error.
    rel
        (Scalar) Relative error.
    """

    def __init__(self, x: Scalar, x0: Scalar):
        """Constructor.

        :param x: Scalar: Measure.
        :param x0: Scalar: Model.
        """
        self.abs: Scalar = abs(x - x0)
        self.rel: Scalar = self.abs / x if x != 0 else Scalar.nan()

    def __str__(self):
        return f"ScalarError(abs={self.abs} rel={self.rel})"


class VectorError:
    """A class containing a Vector values' measurement error.

    Attributes
    ----------
    x
        (ScalarError) A X coordinate's error.
    y
        (ScalarError) A Y coordinate's error.
    value
        (ScalarError) A value's error.
    """

    def __init__(self, vec: Vector, vec0: Vector):
        """Constructor.

        param vec: Vector: Measure.
        vec0: Vector: Model.
        """
        self.x = ScalarError(vec.x, vec0.x)
        self.y = ScalarError(vec.y, vec0.y)
        self.value = ScalarError(vec.value, vec0.value)

    def __str__(self):
        return f"VectorError(x={self.x} y={self.y} value={self.value})"


class Error:
    """A class containing a Result values' measurement errors.

    Attributes
    ----------
    duration
    (ScalarError) A duration's error.
    duration1
    (ScalarError) A duration1's error.
    duration2
    (ScalarError) A duration2's error.
    start_velocity
    (VectorError) A start velocity's error.
    end_velocity
    (VectorError) A end velocity's error.
    reach
    (VectorError) A reach's error.
    """

    def __init__(self, measure: Result, model: Result):
        """Constructor.

        :param measure: Result: Measure.
        :param model: Result: Model.
        """
        self.duration = ScalarError(measure.duration, model.duration)
        self.duration1 = ScalarError(measure.duration1, model.duration1)
        self.duration2 = ScalarError(measure.duration2, model.duration2)
        self.start_velocity = VectorError(measure.start_velocity, model.start_velocity)
        self.end_velocity = VectorError(measure.end_velocity, model.end_velocity)
        self.reach = VectorError(measure.reach, model.reach)

    def __str__(self):
        return (f"Error(duration={self.duration} "
                f"duration1={self.duration1} "
                f"duration2={self.duration2} "
                f"start_velocity={self.start_velocity} "
                f"end_velocity={self.end_velocity} "
                f"reach={self.reach})")


def prepare_errors(measured: list[Result], model: list[Result]) -> list[Error]:
    """Prepares Error list based on Results.

    :param measured: list[Result]: Measured results.
    :param model: list[Result]: Model results.
    :returns: List of errors.
    """
    logging.debug(f"Preparing errors.")
    errors = []
    for i in range(0, len(model)):
        errors.append(Error(measured[i], model[i]))
        logging.debug(f"Prepared error: error={errors[-1]} measured={measured[i]} model={model[i]}")
    logging.info(f"Prepared errors: n={len(errors)}")
    return errors
