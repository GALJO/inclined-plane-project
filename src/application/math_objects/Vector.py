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
from math import sqrt

from application.math_objects.Scalar import Scalar
from infrastructure.config.config import SIM_RESOLUTION


def translate_abs(x: Scalar | float, y: Scalar | float) -> tuple[Scalar | float, Scalar | float]:
    """
    Absolutely translates point in coordinate system starting in bottom-left screen corner
    to point in pygame coordinate system and vice versa. [x, y] vector changes sense, direction and value.
    :param x: point x-coordinate
    :param y: point y-coordinate
    :returns: (x, y) - translated coordinate
    :rtype: tuple[float, float]
    """
    return x, y * -1 + SIM_RESOLUTION[1]


def translate(x: Scalar | float, y: Scalar | float) -> tuple[Scalar | float, Scalar | float]:
    """
    Relatively translates point in coordinate system starting in bottom-left screen corner
    to point in pygame coordinate system and vice versa. [x, y] vector changes only sense and direction.
    :param x: vector x-coordinate
    :param y: vector y-coordinate
    :returns: (x, y) - translated coordinate
    :rtype: tuple[float, float]
    """
    return x, y * (-1)


class Vector:
    """
    A class representing a mathematical vector object.
    Unit of the vector is unit of x, y and value attributes. They should be the same.
    Attributes
    ----------
    x : Scalar
        First coordinate of the vector (x).
    y : Scalar
        Second coordinate of the vector (y).
    value : Scalar
        Value of the vector.
    """

    def __init__(self, _x: Scalar, _y: Scalar):
        """
        Class constructor.
        Parameters
        ----------
        _x: Scalar
            Scalar x coordinate of the vector (unit should be the same as _y).
        _y: Scalar
            Scalar y coordinate of the vector (unit should be the same as _x).
        """
        self.x = _x
        self.y = _y
        self.value = Scalar(sqrt(_x.value ** 2 + _y.value ** 2), _x.unit)

    @classmethod
    def from_float(cls, _x: float, _y: float, _unit: str):
        """
        Creates Vector instance from float coordinates.
        Parameters
        ----------
        _x: float
            Vector x coordinate.
        _y: float
            Vector y coordinate.
        _unit: str
            Unit of the vector.
        Returns
        -------
        vector: Vector
            Vector object.
        """
        return cls(Scalar(_x, _unit), Scalar(_y, _unit))

    def translated(self):
        """
        Relatively translates vector in coordinate system starting in bottom-left screen corner
        to point in pygame coordinate system and vice versa. Vector changes sense, direction and value.
        :returns: Translated Vector.
        """
        x, y = translate(self.x, self.y)
        return Vector(x, y)

    def translated_abs(self):
        """
        Absolutely translates vector in coordinate system starting in bottom-left screen corner
        to point in pygame coordinate system and vice versa. Vector changes only sense and direction.
        :returns: Translated Vector.
        """
        x, y = translate_abs(self.x, self.y)
        return Vector(x, y)

    def __str__(self) -> str:
        """
        Converts to string.
        """
        return f"Vector({self.x}, {self.y} -> {self.value})"

    def __eq__(self, other):
        """
        Defines equality of two Vectors.
        :param other: Other Vector.
        """
        if hasattr(other, "x") and hasattr(other, "y") and hasattr(other, "value"):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __mul__(self, other: Scalar | int | float):
        """
        Defines multiplication of a vector.
        :param other: Numerical or Scalar multiplier.
        """
        if type(other) == Scalar or type(other) == int or type(other) == float:
            return Vector(self.x * other, self.y * other)
        return NotImplemented

    def __abs__(self):
        """
        Defines absolute value.
        """
        return Vector(abs(self.x), abs(self.y))
