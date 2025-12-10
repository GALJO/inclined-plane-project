from math import isnan

from src.Scalar import Scalar
from src.constants import MATH_PRECISION


def test_inits():
    # when
    s = Scalar(5, "kg")
    s2 = Scalar(5)

    # then
    assert s.value == 5
    assert s.unit == "kg"
    assert s2.value == 5
    assert s2.unit is None


def test_inits_zero():
    # when
    s = Scalar(pow(0.1, MATH_PRECISION + 1))
    s2 = Scalar(-pow(0.1, MATH_PRECISION + 1))

    # then
    assert s.value == 0
    assert s2.value == 0


def test_nan():
    # when
    s = Scalar.nan()

    # then
    assert isnan(s.value)
    assert s.unit is None


def test_arithmetic():
    # given
    s = Scalar(2, "kg")
    s2 = Scalar(3, "m")

    # when
    add = s + s2
    sub = s - s2
    mul = s * s2
    div = s / s2

    # then
    assert add.value == 5
    assert add.unit == "kg"

    assert sub.value == -1
    assert sub.unit == "kg"

    assert mul.value == 6
    assert mul.unit == "kg"

    assert round(div.value, 4) == 0.6667
    assert div.unit == "kg"


def test_arithmetic_number():
    # given
    s = Scalar(2, "kg")
    n = 3

    # when
    add = s + n
    sub = s - n
    mul = s * n
    div = s / n

    # then
    assert add.value == 5
    assert add.unit == "kg"

    assert sub.value == -1
    assert sub.unit == "kg"

    assert mul.value == 6
    assert mul.unit == "kg"

    assert round(div.value, 4) == 0.6667
    assert div.unit == "kg"


def test_equality_positive():
    # given
    s = Scalar(2, "kg")
    s2 = Scalar(2, "kg")

    # when then
    assert s == s2


def test_inequality():
    # given
    s = Scalar(2, "kg")
    s2 = Scalar(3, "kg")
    s3 = Scalar(2, "m")

    # when then
    assert s != s2
    assert s != s3


def test_equality_number():
    # given
    s = Scalar(2, "kg")
    n = 2

    # when then
    assert s == n


def test_inequality_number():
    # given
    s = Scalar(2, "kg")
    n = 5

    # when then
    assert s != n


def test_ordering():
    # given
    s = Scalar(5)
    s2 = Scalar(10)
    s3 = Scalar(1)

    # when then
    assert s < s2
    assert s > s3

def test_ordering_negative():
    # given
    s = Scalar(5)
    s2 = Scalar(10)
    s3 = Scalar(1)

    # when then
    assert not s > s2
    assert not s < s3


def test_ordering_number():
    # given
    s = Scalar(5)
    n = 10
    n2 = 1

    # when then
    assert s < n
    assert s > n2


def test_ordering_number_negative():
    # given
    s = Scalar(5)
    n = 10
    n2 = 1

    # when then
    assert not s > n
    assert not s < n2