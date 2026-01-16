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
import functools
from math import nan

from infrastructure.config.config import CONFIG


@functools.total_ordering
class Scalar:
    """A class representing a scalar value.

    Attributes
    ----------
    value
        (float) Value.
    unit
        (str | None) Unit.
    """

    def __init__(self, value: float, unit: str | None = None):
        """
        Constructor.
        :param value: float: Numerical value of the scalar. Its being rounded to amount of decimal places set in config.
        :param unit: str | None: Unit (default None).
        """
        self.value: float = round(value, CONFIG.math_precision)
        self.unit: str | None = unit

    @classmethod
    def nan(cls):
        """Creates a nan (not a number) scalar.

        :returns: A nan scalar.
        """
        return Scalar(nan)

    def __add__(self, other):
        """Defines addition.

        :param other: Operand (Scalar instance or numerical).
        """
        if is_number(other):
            return Scalar(self.value + other, self.unit)
        elif is_scalar(other):
            return Scalar(self.value + other.value, self.unit)
        return NotImplemented

    def __sub__(self, other):
        """Defines substraction.

        :param other: Operand (Scalar instance or numerical).
        """
        if is_number(other):
            return Scalar(self.value - other, self.unit)
        elif is_scalar(other):
            return Scalar(self.value - other.value, self.unit)
        return NotImplemented

    def __mul__(self, other):
        """Defines multiplication.

        :param other: Operand (Scalar instance or numerical).
        """
        if is_number(other):
            return Scalar(self.value * other, self.unit)
        elif is_scalar(other):
            return Scalar(self.value * other.value, self.unit)
        return NotImplemented

    def __abs__(self):
        """Defines absolute value."""
        return Scalar(abs(self.value), self.unit)

    def __truediv__(self, other):
        """Defines division.

        :param other: Operand (Scalar instance or numerical).
        """
        if is_number(other):
            return Scalar(self.value / other, self.unit)
        elif is_scalar(other):
            return Scalar(self.value / other.value, self.unit)
        return NotImplemented

    def __eq__(self, other):
        """Defines equality.

        :param other: Operand (Scalar instance or numerical).
        """
        if is_number(other):
            return self.value == round(other, CONFIG.math_precision)
        elif is_scalar(other):
            return self.value == other.value and self.unit == other.unit
        return NotImplemented

    def __lt__(self, other):
        """Defines lower than.

        :param other: Operand (Scalar instance or numerical).
        """
        if is_number(other):
            return self.value < round(other, CONFIG.math_precision)
        elif is_scalar(other):
            return self.value < other.value
        return NotImplemented

    def __str__(self):
        return f"{self.value}{self.unit}" if self.unit is not None else f"{self.value}"


def is_number(o) -> bool:
    """Checks if a variable is a numerical.

    :param o: A checked variable.
    :returns: True if o is numerical, False otherwise.
    """
    if type(o) == int or type(o) == float:
        return True
    return False


def is_scalar(o):
    """Checks if a variable is a Scalar instance.

    :param o: A checked variable.
    :returns: True if o is a Scalar instance, False otherwise.
    """
    if hasattr(o, "value") and hasattr(o, "unit"):
        return True
    return False
