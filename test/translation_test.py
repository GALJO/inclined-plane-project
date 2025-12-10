from src.Scalar import Scalar
from src.Vector import translate, translate_abs
from src.constants import RESOLUTION


def test_translation_scalar():
    # given
    x = Scalar(5, "m")
    y = Scalar(6)
    model = (Scalar(5, "m"), Scalar(-6))

    # when then
    assert model == translate(x, y)


def test_translation_number():
    # given
    x = 5
    y = 6
    model = (5, -6)

    # when then
    assert model == translate(x, y)


def test_absolute_translation_scalar():
    # given
    x = Scalar(5, "m")
    y = Scalar(6)
    model = (Scalar(5, "m"), Scalar(-6 + RESOLUTION[1]))

    # when then
    assert model == translate_abs(x, y)


def test_absolute_translation_number():
    # given
    x = 5
    y = 6
    model = (5, -6 + RESOLUTION[1])

    # when then
    assert model == translate_abs(x, y)
