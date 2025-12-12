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

from infrastructure.constants import MATH_PRECISION


def is_number(o) -> bool:
    """
    Checks if operand is a number.
    :param o: Operand.
    :returns: True if o is number, False otherwise.
    """
    if type(o) == int or type(o) == float:
        return True
    return False


def is_scalar(o):
    """
    Checks if operand is a Scalar.
    :param o: Operand.
    :returns: True if o is Scalar, False otherwise.
    """
    if hasattr(o, "value") and hasattr(o, "unit"):
        return True
    return False


@functools.total_ordering
class Scalar:
    """
    A class defining scalar value.
    Attributes
    ----------
    value : float
        Numeric value of scalar. It is defined as 0 if value absolute is lower or equal to D constant value.
    unit : str | None
        Unit of scalar (can be None).
    """

    def __init__(self, _value: float, _unit: str | None = None):
        """
        Class constructor.
        Parameters
        ----------
        _value: float
            Numerical value of the scalar.
            If given value absolute is lower or equal to D constant value it is treated as 0.
        _unit: str
            Unit of the Scalar (default None).
        """
        self.value = round(_value, MATH_PRECISION)
        self.unit = _unit

    @classmethod
    def nan(cls):
        """
        Creates nan (not a number) scalar.
        :returns: "Nan" scalar (no unit).
        """
        return Scalar(nan)

    def __add__(self, other):
        """
        Defines addition.
        :param other: Operand (Scalar of number).
        """
        if is_number(other):
            return Scalar(self.value + other, self.unit)
        elif is_scalar(other):
            return Scalar(self.value + other.value, self.unit)
        else:
            return NotImplemented

    def __sub__(self, other):
        """
        Defines substraction.
        :param other: Operand (Scalar of number).
        """
        if is_number(other):
            return Scalar(self.value - other, self.unit)
        elif is_scalar(other):
            return Scalar(self.value - other.value, self.unit)
        else:
            return NotImplemented

    def __mul__(self, other):
        """
        Defines multiplication.
        :param other: Operand (Scalar of number).
        """
        if is_number(other):
            return Scalar(self.value * other, self.unit)
        elif is_scalar(other):
            return Scalar(self.value * other.value, self.unit)
        else:
            return NotImplemented

    def __abs__(self):
        """
        Defines Scalar absolute value.
        """
        return Scalar(abs(self.value), self.unit)

    def __truediv__(self, other):
        """
        Defines division.
        :param other: Operand (Scalar of number).
        """
        if is_number(other):
            return Scalar(self.value / other, self.unit)
        elif is_scalar(other):
            return Scalar(self.value / other.value, self.unit)
        else:
            return NotImplemented

    def __eq__(self, other):
        """
        Defines equal.
        :param other: Operand (Scalar of number).
        """
        if is_number(other):
            return self.value == round(other, MATH_PRECISION)
        elif is_scalar(other):
            return self.value == other.value and self.unit == other.unit
        else:
            return NotImplemented

    def __lt__(self, other):
        """
        Defines lower than.
        :param other: Operand (Scalar of number).
        """
        if is_number(other):
            return self.value < round(other, MATH_PRECISION)
        elif is_scalar(other):
            return self.value < other.value
        else:
            return NotImplemented


    def __str__(self):
        return f"{self.value}{self.unit}" if self.unit is not None else f"{self.value}"
