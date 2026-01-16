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

from application.math.math_util import translate_abs, translate
from application.math.scalar import Scalar


class Vector:
    """A class representing a mathematical vector value.

    Attributes
    ----------
    x
        (Scalar) First coordinate of a vector.
    y
        (Scalar) Second coordinate of a vector.
    value
        (Scalar) Value (module) of a vector.
    """

    def __init__(self, x: Scalar, y: Scalar):
        """Constructor.

        :param x: Scalar: First coordinate of a vector.
        :param y: Scalar: Second coordinate of a vector.
        """
        self.x = x
        self.y = y
        self.value = Scalar(sqrt(x.value ** 2 + y.value ** 2), x.unit)

    @classmethod
    def from_float(cls, x: float, y: float, unit: str | None):
        """Creates Vector instance from numerical variables.

        :param x: float: Vector x coordinate.
        :param y: float: Vector y coordinate.
        :param unit: str | None: Vector unit.
        """
        return cls(Scalar(x, unit), Scalar(y, unit))

    def translated(self):
        """Returns translated vector using translate math_util method."""
        x, y = translate(self.x, self.y)
        return Vector(x, y)

    def translated_abs(self):
        """Returns translated vector using translate_abs math_util method."""
        x, y = translate_abs(self.x, self.y)
        return Vector(x, y)

    def __str__(self) -> str:
        return f"Vector({self.x}, {self.y} -> {self.value})"

    def __eq__(self, other):
        """Defines equality of two Vectors.

        :param other: Other Vector.
        """
        if hasattr(other, "x") and hasattr(other, "y") and hasattr(other, "value"):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __mul__(self, other: Scalar | int | float):
        """Defines multiplication of a vector.

        :param other: Operand (Scalar instance or numerical)
        """
        if type(other) == Scalar or type(other) == int or type(other) == float:
            return Vector(self.x * other, self.y * other)
        return NotImplemented

    def __abs__(self):
        """Defines absolute value."""
        return Vector(abs(self.x), abs(self.y))
