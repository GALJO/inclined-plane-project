from application.math.scalar import Scalar
from infrastructure.config.config import CONFIG


def translate_abs(x: Scalar | float, y: Scalar | float) -> tuple[Scalar | float, Scalar | float]:
    """Absolutely translates point from/to coordinate system starting in bottom-left corner of the screem
    to/from coordinate system starting in upper-left corner of the screen. The (x y) vector changes its value.

    :param x: Scalar | float: X coordinate
    :param y: Scalar | float: X coordinate
    :returns: (x, y) - translated coordinates
    :rtype: tuple[float, float]

    """
    return x, y * -1 + CONFIG.resolution[1]


def translate(x: Scalar | float, y: Scalar | float) -> tuple[Scalar | float, Scalar | float]:
    """Relatively translates point from/to coordinate system starting in bottom-left corner of the screem
    to/from coordinate system starting in upper-left corner of the screen. The (x y) vector saves its value.

    :param x: Scalar | float: X coordinate
    :param y: Scalar | float: X coordinate
    :returns: (x, y) - translated coordinates
    :rtype: tuple[float, float]

    """
    return x, y * (-1)
