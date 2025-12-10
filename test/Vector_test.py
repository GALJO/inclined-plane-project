from math import sqrt

from application.scalar.Scalar import Scalar
from application.math_objects.Vector import Vector


def test_init():
    v = Vector(Scalar(5), Scalar(5))

    assert v.x == 5
    assert v.y == 5
    assert round(v.value.value, 4) == round(sqrt((5 ** 2) * 2), 4)
    assert v.value.unit is None


def test_equality():
    v = Vector(Scalar(5, "m"), Scalar(5, "m"))
    v1 = Vector(Scalar(5, "m"), Scalar(5, "m"))

    assert v == v1


def test_inequality():
    v = Vector(Scalar(5, "m"), Scalar(5, "m"))
    v1 = Vector(Scalar(5, "kg"), Scalar(5, "m"))
    v2 = Vector(Scalar(6, "m"), Scalar(5, "m"))
    v3 = Vector(Scalar(5, "m"), Scalar(6, "m"))

    assert v != v1
    assert v != v2
    assert v != v3


def test_from_float():
    v = Vector.from_float(2, 3, "kg")

    assert v.x == 2
    assert v.y == 3
    assert round(v.value.value, 4) == round(sqrt((2 ** 2) + (3 ** 2)), 4)

    assert v.x.unit == "kg"
    assert v.y.unit == "kg"
